"""Ingestion: raw sources -> retrieval index + Gemma-written wiki pages + index.md.

Re-ingesting is idempotent. index/manifest.json maps every source section to
the note it produced, so an unchanged section is skipped, a changed one
rewrites the *same* note file, and no duplicate or machine-named notes appear.
Notes marked `reviewed: true` in their front matter are never overwritten.
"""

import datetime as dt
import json
import re
import time
from pathlib import Path

import numpy as np

from . import config, llm
from .retrieval import Embedder, Index, chunk_section
from .sources import Section, list_sources, load_sections

MANIFEST = config.INDEX_DIR / "manifest.json"
GENERIC_TITLES = {"overview", "case", "notes", "summary", "cheat sheet", "introduction", "readings"}


# ---------------------------------------------------------------- manifest

def _load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {"sections": {}, "notes": {}}


def _save_manifest(m: dict):
    config.INDEX_DIR.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------- Gemma page drafts

def _prompt_for(section: Section) -> list[dict]:
    rules = (config.PROMPTS_DIR / "ingest-instructions.md").read_text()
    body = section.text[: config.NOTE_SECTION_MAX_CHARS]
    return [
        {"role": "system", "content": rules},
        {"role": "user", "content":
            f"Course: {section.course}\nSource file: {section.path}\nSection heading: {section.title}\n\n"
            f"--- SECTION TEXT ---\n{body}\n--- END ---"},
    ]


def _parse_draft(text: str) -> dict:
    """Parse the TITLE/SUMMARY/KEY POINTS/KEY TERMS block; tolerate small format slips."""
    def field(name):
        m = re.search(rf"^\**{name}\**\s*:\s*(.+)$", text, re.M | re.I)
        return m.group(1).strip() if m else ""

    points_block = re.search(r"KEY POINTS\**\s*:?\s*\n(.*?)(?:\n\**KEY TERMS|\Z)", text, re.S | re.I)
    points = []
    if points_block:
        points = [re.sub(r"^\s*[-*•]\s*", "", l).strip()
                  for l in points_block.group(1).splitlines() if re.match(r"^\s*[-*•]\s+\S", l)]
    terms = [t.strip(" .") for t in re.split(r"[;,]", field("KEY TERMS")) if t.strip(" .")]
    return {"title": field("TITLE"), "summary": field("SUMMARY"), "key_points": points[:8],
            "key_terms": terms[:8]}


def _clean_title(title: str, fallback: str) -> str:
    t = re.sub(r"[\"“”'`*#\[\]|^:\\/<>?]", "", title).strip(" .-–—")
    t = re.sub(r"\s+", " ", t)
    if not t or t.lower() in GENERIC_TITLES or len(t.split()) > 6:
        t = re.sub(r"[\"“”'`*#\[\]|^:\\/<>?]", "", fallback).strip(" .-–—")
        t = " ".join(t.split()[:6])
    return t[:1].upper() + t[1:]


# ---------------------------------------------------------------- note assembly

def _note_path(course: str, title: str) -> str:
    return f"{course}/{title}.md"


def _find_merge_target(m: dict, course: str, title: str, title_vecs: dict) -> str | None:
    """Same subject in the same course (e.g. 'Product Life Cycle' twice) -> one merged note."""
    candidates = [p for p, n in m["notes"].items() if n["course"] == course]
    for p in candidates:
        if m["notes"][p]["title"].lower() == title.lower():
            return p
    if not candidates:
        return None
    q = Embedder.encode([title])[0]
    best, best_sim = None, 0.0
    for p in candidates:
        if p not in title_vecs:
            title_vecs[p] = Embedder.encode([m["notes"][p]["title"]])[0]
        sim = float(title_vecs[p] @ q)
        if sim > best_sim:
            best, best_sim = p, sim
    return best if best_sim >= config.NOTE_MERGE_SIM else None


def _unique_title(m: dict, course: str, title: str) -> str:
    """Wikilinks resolve by file name, so titles must be unique across course folders."""
    clash = any(n["title"].lower() == title.lower() and n["course"] != course for n in m["notes"].values())
    return f"{title} - {course}" if clash else title


def _source_ref(section: Section) -> dict:
    return {"section_id": section.section_id, "path": section.path, "section": section.title,
            "page": section.page}


def _upsert_note(m: dict, section: Section, draft: dict, title_vecs: dict) -> str:
    prev = m["sections"].get(section.section_id, {}).get("note")
    if prev and prev in m["notes"]:
        path = prev                                   # stable file name on re-ingest
        note = m["notes"][path]
        if len(note["sources"]) == 1:                 # note owned by this section only: replace content
            note.update(summary=draft["summary"], key_points=draft["key_points"],
                        key_terms=draft["key_terms"])
        else:
            _merge_into(note, draft)
    else:
        title = _clean_title(draft["title"], section.title)
        path = _find_merge_target(m, section.course, title, title_vecs)
        if path:
            _merge_into(m["notes"][path], draft)
        else:
            title = _unique_title(m, section.course, title)
            path = _note_path(section.course, title)
            m["notes"][path] = {"title": title, "course": section.course, "summary": draft["summary"],
                                "key_points": draft["key_points"], "key_terms": draft["key_terms"],
                                "sources": []}
    note = m["notes"][path]
    note["sources"] = [s for s in note["sources"] if s["section_id"] != section.section_id]
    note["sources"].append(_source_ref(section))
    return path


def _merge_into(note: dict, draft: dict):
    seen = {p.lower() for p in note["key_points"]}
    note["key_points"] += [p for p in draft["key_points"] if p.lower() not in seen][:4]
    note["key_terms"] = list(dict.fromkeys(note["key_terms"] + draft["key_terms"]))[:10]
    if not note["summary"]:
        note["summary"] = draft["summary"]


# ---------------------------------------------------------------- consolidation

def _consolidate(m: dict, log=print) -> int:
    """Merge notes that describe the same subject (e.g. the same case summarized in two places).

    Embeddings propose candidate pairs in the same course; Gemma makes the call, because
    similarity alone cannot tell "Teams vs Zoom" twice apart from "Monopoly" vs "Oligopoly".
    Decisions are cached in the manifest so re-ingesting does not ask again.
    """
    checks = m.setdefault("merge_checks", {})
    paths = list(m["notes"])
    if len(paths) < 2:
        return 0
    notes = m["notes"]
    vecs = Embedder.encode([f"{notes[p]['title']}. {notes[p]['summary']}" for p in paths])
    sims = vecs @ vecs.T
    pairs = sorted(((float(sims[i, j]), paths[i], paths[j]) for i in range(len(paths))
                    for j in range(i + 1, len(paths))
                    if notes[paths[i]]["course"] == notes[paths[j]]["course"]
                    and sims[i, j] >= config.MERGE_CANDIDATE_SIM), reverse=True)
    merged = 0
    for sim, a, b in pairs:
        if a not in notes or b not in notes:          # already merged away in this pass
            continue
        key = " || ".join(sorted([notes[a]["title"], notes[b]["title"]]))
        if key not in checks:
            q = [{"role": "user", "content":
                  "Two wiki notes from the same MBA course:\n\n"
                  f"A: {notes[a]['title']}: {notes[a]['summary']}\n\n"
                  f"B: {notes[b]['title']}: {notes[b]['summary']}\n\n"
                  "Are A and B about the same subject (the same concept, framework, reading or case), "
                  "so that a reader would expect a single wiki page? Answer only YES or NO."}]
            checks[key] = llm.generate(q, max_tokens=4).text.strip().upper().startswith("YES")
        if checks[key]:
            keep, drop = (a, b) if len(notes[a]["sources"]) >= len(notes[b]["sources"]) else (b, a)
            _merge_into(notes[keep], notes[drop])
            notes[keep]["sources"] += notes[drop]["sources"]
            for sid in m["sections"]:
                if m["sections"][sid]["note"] == drop:
                    m["sections"][sid]["note"] = keep
            del notes[drop]
            merged += 1
            log(f"  merged '{drop.split('/')[-1][:-3]}' into '{keep.split('/')[-1][:-3]}' (similarity {sim:.2f})")
    return merged


# ---------------------------------------------------------------- links, files, index.md

def _related(m: dict, log=print) -> dict[str, list[tuple[str, str]]]:
    """Embeddings propose neighbours; Gemma explains each link in one line or rejects it.

    Reasons are cached in the manifest (keyed by the two titles), so re-ingesting is fast.
    """
    paths = list(m["notes"])
    notes = m["notes"]
    cache = m.setdefault("link_reasons", {})
    if len(paths) < 2:
        return {p: [] for p in paths}
    vecs = Embedder.encode([f"{notes[p]['title']}. {notes[p]['summary']}" for p in paths])
    sims = vecs @ vecs.T
    np.fill_diagonal(sims, -1)
    out, asked = {}, 0
    for i, p in enumerate(paths):
        cands = [j for j in np.argsort(-sims[i]) if sims[i, j] >= config.RELATED_MIN_SIM][: config.RELATED_NOTES + 1]
        links = []
        for j in cands:
            q = paths[j]
            key = f"{notes[p]['title']} -> {notes[q]['title']}"
            if key not in cache:
                cache[key] = _link_reason(notes[p], notes[q])
                asked += 1
            if cache[key] and len(links) < config.RELATED_NOTES:
                links.append((q, cache[key]))
        out[p] = links
    if asked:
        log(f"  wrote {asked} new link explanations")
    return out


def _link_reason(a: dict, b: dict) -> str | None:
    prompt = [{"role": "user", "content":
               f"Page 1: \"{a['title']}\" ({a['course']}): {a['summary']}\n"
               f"Page 2: \"{b['title']}\" ({b['course']}): {b['summary']}\n\n"
               f"Write one short sentence (max 18 words) for a \"Related notes\" list on page 1, explaining "
               f"what \"{b['title']}\" adds for someone reading about {a['title']}. Name the concepts, "
               "never write \"page 1\", \"page 2\", \"note A\" or \"note B\". Start with a verb such as "
               "Applies, Contrasts, Extends, Explains or Gives. If the two subjects have no real connection, "
               "answer only UNRELATED."}]
    text = llm.generate(prompt, max_tokens=40).text.strip().strip('"').splitlines()[0]
    return None if not text or "UNRELATED" in text.upper() else text.rstrip(".") + "."


def _link_to_source(src: dict) -> str:
    target = "../../" + src["path"] + (f"#page={src['page']}" if src.get("page") else "")
    label = src["path"].split("/")[-1] + " › " + src["section"] + (f" (p.{src['page']})" if src.get("page") else "")
    return f"- [{label}]({target})"


def _render_note(note: dict, related: list[tuple[str, str]], m: dict) -> str:
    fm = [
        "---",
        f"title: \"{note['title']}\"",
        f"course: {note['course']}",
        "sources:",
        *[f"  - \"{s['path']}#{s['section']}\"" for s in note["sources"]],
        "source_ids:",
        *[f"  - {s['section_id']}" for s in note["sources"]],
        f"key_terms: [{', '.join(json.dumps(t, ensure_ascii=False) for t in note['key_terms'])}]",
        f"generated_by: {config.LLM_MODEL}",
        f"ingested: {dt.date.today().isoformat()}",
        "reviewed: false",
        "---",
    ]
    body = [f"# {note['title']}", "", note["summary"] or "_No summary generated._", "", "## Key points", ""]
    body += [f"- {p}" for p in note["key_points"]] or ["- _None extracted._"]
    body += ["", "## Related notes", ""]
    body += [f"- [[{m['notes'][p]['title']}]]: {why}" for p, why in related] or ["- _No closely related notes._"]
    body += ["", "## Sources", ""] + [_link_to_source(s) for s in note["sources"]]
    return "\n".join(fm + body) + "\n"


def _is_reviewed(path: Path) -> bool:
    return path.exists() and re.search(r"^reviewed:\s*true\s*$", path.read_text(), re.M) is not None


def _write_notes(m: dict, related: dict):
    config.WIKI_DIR.mkdir(parents=True, exist_ok=True)
    expected = set()
    for rel, note in m["notes"].items():
        path = config.WIKI_DIR / rel
        expected.add(path.resolve())
        if _is_reviewed(path):
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_render_note(note, related.get(rel, []), m), encoding="utf-8")
    # Generated notes no longer produced by any source are removed. Hand-written notes
    # (no `generated_by:` field) and reviewed notes are never touched.
    for path in config.WIKI_DIR.rglob("*.md"):
        if path.resolve() in expected or _is_reviewed(path):
            continue
        if re.search(r"^generated_by:", path.read_text(), re.M):
            path.unlink()
    for d in sorted(config.WIKI_DIR.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()


def _write_index(m: dict):
    by_course: dict[str, list[dict]] = {}
    for note in m["notes"].values():
        by_course.setdefault(note["course"], []).append(note)
    lines = [
        "# Index",
        "",
        "Personal wiki of my Berkeley Haas MBA course notes, organized by course.",
        "Each page summarizes one subject, links to related pages, and points back to the",
        "original notes in `raw/`, which are never edited.",
        "",
    ]
    for course in sorted(by_course):
        lines += [f"## {course}", ""]
        for note in sorted(by_course[course], key=lambda n: n["title"].lower()):
            first = re.split(r"(?<=[.!?])\s", note["summary"].strip())[0] if note["summary"] else ""
            lines.append(f"- [[{note['title']}]]: {first}")
        lines.append("")
    lines += ["## Original sources", ""]
    for p in list_sources():
        lines.append(f"- [{p.name}](raw/{p.name})")
    config.INDEX_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- entry point

def ingest(target: Path | None = None, force: bool = False, skip_notes: bool = False, log=print) -> dict:
    t0 = time.perf_counter()
    files = list_sources(target)
    if not files:
        raise FileNotFoundError(f"No .md, .txt or .pdf sources found in {target or config.RAW_DIR}")
    full_run = target is None or target.resolve() == config.RAW_DIR.resolve()

    sections: list[Section] = []
    for f in files:
        secs = load_sections(f)
        log(f"  read {f.name}: {len(secs)} sections")
        sections += secs

    # 1) retrieval index over original passages
    chunks = [c for s in sections for c in chunk_section(s)]
    if full_run or not Index.exists():
        index = Index.build(chunks)
    else:
        index = Index.load().replace_sources({f.stem for f in files}, chunks)
    index.save()
    log(f"  indexed {len(chunks)} passages ({len(index.chunks)} total in index)")

    # 2) wiki pages written by Gemma
    m = _load_manifest()
    generated = skipped = merged = 0
    gen_seconds = []
    if not skip_notes:
        title_vecs: dict = {}
        present = {s.section_id for s in sections}
        scope = {f.stem for f in files}
        # sections of in-scope sources that disappeared: detach them from their notes
        for sid in [sid for sid in m["sections"] if sid.split("#")[0] in scope and sid not in present]:
            note = m["notes"].get(m["sections"].pop(sid)["note"])
            if note:
                note["sources"] = [s for s in note["sources"] if s["section_id"] != sid]
        for i, s in enumerate(sections, 1):
            known = m["sections"].get(s.section_id)
            if known and known["digest"] == s.digest and known["note"] in m["notes"] and not force:
                skipped += 1
                continue
            gen = llm.generate(_prompt_for(s), max_tokens=config.MAX_TOKENS_INGEST)
            gen_seconds.append(gen.seconds)
            draft = _parse_draft(gen.text)
            path = _upsert_note(m, s, draft, title_vecs)
            m["sections"][s.section_id] = {"digest": s.digest, "note": path}
            generated += 1
            log(f"  [{i}/{len(sections)}] {s.path} › {s.title[:40]}  ->  wiki/{path}  ({gen.seconds}s)")
        m["notes"] = {p: n for p, n in m["notes"].items() if n["sources"]}
        merged = _consolidate(m, log)
        related = _related(m, log)
        _save_manifest(m)
        _write_notes(m, related)
        _write_index(m)

    stats = {
        "files": [f.name for f in files],
        "sections": len(sections),
        "passages_indexed": len(chunks),
        "notes_generated_or_updated": generated,
        "sections_unchanged_skipped": skipped,
        "notes_merged": merged,
        "wiki_notes_total": len(m["notes"]),
        "seconds_total": round(time.perf_counter() - t0, 1),
        "seconds_per_note_avg": round(sum(gen_seconds) / len(gen_seconds), 2) if gen_seconds else None,
        "peak_process_memory_gb": llm.process_rss_gb(),
    }
    return stats
