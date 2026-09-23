"""The three interaction modes. The harness, not the model, decides what each one sees.

search: retrieval tool only. Returns original passages; no language model involved.
ask:    RAG. Fresh context every time (no chat history, no persona), research rules,
        numbered evidence, citation check.
chat:   persona + recent conversation. Retrieves notes only when the turn needs them.
"""

import re

from . import config, evidence, llm
from .retrieval import Hit, Index

_index = None


def _get_index(with_vectors: bool = True) -> Index:
    global _index
    if _index is None or (with_vectors and _index.vectors is None):
        _index = Index.load(with_vectors=with_vectors)
    return _index


def _hit_dict(h: Hit) -> dict:
    return {"location": h.chunk.location(), "path": h.chunk.path, "section": h.chunk.section,
            "page": h.chunk.page, "score": round(h.score, 5), "cosine": round(h.cosine, 4),
            "bm25": round(h.bm25, 3), "text": h.chunk.text}


def _evidence_block(hits: list[Hit], label: str) -> str:
    return "\n\n".join(f"[{label}{i}] ({h.chunk.location()})\n{h.chunk.text}" for i, h in enumerate(hits, 1))


# ================================================================ search

def search(query: str, k: int = config.TOP_K_SEARCH, keyword_only: bool = False, save: bool = True) -> dict:
    hits = _get_index(with_vectors=not keyword_only).search(query, k, keyword_only=keyword_only)
    result = {"mode": "search", "query": query,
              "method": "bm25" if keyword_only else "hybrid (bm25 + embeddings, RRF)",
              "passages": [_hit_dict(h) for h in hits]}
    if save:
        md = f"# Search: {query}\n\nMethod: {result['method']}. No answer is generated in search mode.\n\n"
        result["saved_to"] = evidence.save("search", query, result, md + evidence.passages_md(result["passages"], "P"))
    return result


# ================================================================ ask

INSUFFICIENT = "insufficient evidence"
SUPPORT_MIN = 0.5      # share of a sentence's content words that must appear in its cited passages


def ask(question: str, k: int = config.TOP_K_ASK, save: bool = True) -> dict:
    """Two-step RAG: (1) Gemma quotes the evidence verbatim, the harness verifies every quote;
    (2) Gemma answers from the verified quotes only. Standalone: no chat history, no persona."""
    hits = _get_index().search(question, k)

    # step 1: extract quotes
    extract_rules = (config.PROMPTS_DIR / "extract-instructions.md").read_text()
    g1 = llm.generate([
        {"role": "system", "content": extract_rules},
        {"role": "user", "content": f"Question: {question}\n\nPassages:\n\n{_evidence_block(hits, 'S')}"},
    ], max_tokens=config.MAX_TOKENS_ASK)
    quotes, rejected = verify_quotes(g1.text, hits)

    # step 2: answer from verified quotes (skipped when nothing verifiable was found)
    if quotes:
        rules = (config.PROMPTS_DIR / "wiki-instructions.md").read_text()
        quote_block = "\n".join(f"[S{q['id']}] ({hits[q['id'] - 1].chunk.location()}) \"{q['text']}\"" for q in quotes)
        g2 = llm.generate([
            {"role": "system", "content": rules},
            {"role": "user", "content": f"Question: {question}\n\nVerified quotes:\n{quote_block}"},
        ], max_tokens=config.MAX_TOKENS_ASK)
        answer, gens = g2.text, [g1, g2]
    else:
        answer, gens = ("Insufficient evidence: none of the retrieved passages contains a sentence "
                        "that answers this question."), [g1]

    check = check_citations(answer, len(hits))
    check["weakly_supported"] = support_check(answer, hits)
    result = {
        "mode": "ask", "question": question, **llm.model_identity(),
        "retrieved": [_hit_dict(h) for h in hits],
        "extracted_quotes": [{"id": f"S{q['id']}", "location": hits[q['id'] - 1].chunk.location(),
                              "text": q["text"]} for q in quotes],
        "rejected_quotes": rejected,
        "answer": answer,
        "citations": [{"id": f"S{n}", "location": hits[n - 1].chunk.location()} for n in check["valid"]],
        "citation_check": check,
        "timing": {"generation_seconds": round(sum(g.seconds for g in gens), 2),
                   "steps": [g.seconds for g in gens],
                   "prompt_tokens": sum(g.prompt_tokens for g in gens),
                   "output_tokens": sum(g.output_tokens for g in gens),
                   "tokens_per_sec": gens[-1].tokens_per_sec,
                   "mlx_peak_memory_gb": max(g.peak_memory_gb for g in gens),
                   "process_peak_rss_gb": llm.process_rss_gb()},
    }
    if save:
        result["saved_to"] = evidence.save("ask", question, result, _ask_md(result))
    return result


def _norm(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", re.sub(r"[*_`>|]", " ", text)).strip().lower()


def verify_quotes(text: str, hits: list[Hit]) -> tuple[list[dict], list[dict]]:
    """Keep only quotes that really occur in the passage they claim (exact, or ≥90% of words in order)."""
    quotes, rejected, seen = [], [], set()
    for line in text.splitlines():
        m = re.match(r'^\s*[-*]?\s*\[S(\d+)\]\s*[:\-]?\s*["“]?(.+?)["”]?\s*$', line)
        if not m:
            continue
        n, quote = int(m.group(1)), m.group(2).strip()
        if not 1 <= n <= len(hits):
            rejected.append({"id": f"S{n}", "text": quote, "why": "passage not retrieved"})
            continue
        q, passage = _norm(quote), _norm(hits[n - 1].chunk.text)
        words = q.split()
        ok = q in passage
        if not ok and len(words) >= 4:            # tolerate small copy slips (punctuation, one word)
            import difflib
            sm = difflib.SequenceMatcher(None, passage, q, autojunk=False)
            ok = sum(b.size for b in sm.get_matching_blocks()) >= 0.9 * len(q)
        if ok and (n, q) not in seen:
            seen.add((n, q))
            quotes.append({"id": n, "text": quote})
        elif not ok:
            rejected.append({"id": f"S{n}", "text": quote, "why": "not found verbatim in the passage"})
    return quotes, rejected


def check_citations(answer: str, n_passages: int) -> dict:
    # accepts [S1], [S1, S4] and [S1][S2]
    groups = re.findall(r"\[((?:S\d+\s*,?\s*)+)\]", answer)
    cited = sorted({int(n) for g in groups for n in re.findall(r"S(\d+)", g)})
    valid = [c for c in cited if 1 <= c <= n_passages]
    invalid = [c for c in cited if c not in valid]
    insufficient = answer.strip().lower().startswith(INSUFFICIENT)
    if insufficient:
        status = "insufficient_evidence"
    elif invalid:
        status = "invalid_citation"
    elif not valid:
        status = "uncited_answer"
    else:
        status = "answered_with_citations"
    return {"status": status, "valid": valid, "invalid": invalid}


def _stems(text: str) -> set[str]:
    from .retrieval import tokenize
    return {t[:5] for t in tokenize(text)}


def support_check(answer: str, hits: list[Hit]) -> list[dict]:
    """Flag cited sentences whose content words mostly do not appear in the passages they cite.
    A cheap, local signal that a claim may be blended or invented; a human still reviews it."""
    flagged = []
    for sent in re.split(r"(?<=[.!?])\s+|\n+", answer):
        ids = [int(n) for g in re.findall(r"\[((?:S\d+\s*,?\s*)+)\]", sent) for n in re.findall(r"S(\d+)", g)]
        ids = [i for i in ids if 1 <= i <= len(hits)]
        words = _stems(re.sub(r"\[[^\]]*\]", "", sent))
        if not ids or len(words) < 3:
            continue
        source = set().union(*(_stems(hits[i - 1].chunk.text) for i in ids))
        share = len(words & source) / len(words)
        if share < SUPPORT_MIN:
            flagged.append({"sentence": sent.strip(), "cited": [f"S{i}" for i in ids], "overlap": round(share, 2)})
    return flagged


def _ask_md(r: dict) -> str:
    cites = "\n".join(f"- [{c['id']}] `{c['location']}`" for c in r["citations"]) or "- none"
    quotes = "\n".join(f"- [{q['id']}] `{q['location']}`: \"{q['text']}\"" for q in r["extracted_quotes"]) or "- none"
    rejected = "\n".join(f"- [{q['id']}] \"{q['text']}\" ({q['why']})" for q in r["rejected_quotes"]) or "- none"
    weak = "\n".join(f"- \"{w['sentence']}\" cites {', '.join(w['cited'])}, word overlap {w['overlap']}"
                     for w in r["citation_check"]["weakly_supported"]) or "- none"
    t = r["timing"]
    return (
        f"# Ask: {r['question']}\n\n"
        f"- Model: `{r['model']}` ({r['quantization']}), runtime {r['runtime']}, execution: **{r['execution']}**\n"
        f"- Embeddings: `{r['embedding_model']}`\n"
        f"- Citation check: **{r['citation_check']['status']}**, weakly supported sentences: "
        f"{len(r['citation_check']['weakly_supported'])}\n"
        f"- Generation: {t['generation_seconds']} s (steps {t['steps']}), {t['prompt_tokens']} prompt tokens, "
        f"{t['output_tokens']} output tokens, MLX peak memory {t['mlx_peak_memory_gb']} GB\n\n"
        f"## Answer\n\n{r['answer']}\n\n## Citations\n\n{cites}\n\n"
        f"## Step 1: verified quotes\n\n{quotes}\n\nRejected quotes:\n{rejected}\n\n"
        f"## Support check\n\n{weak}\n\n"
        f"## Retrieved passages\n\n{evidence.passages_md(r['retrieved'], 'S')}"
    )


# ================================================================ chat

# Turns that never need the notes: capabilities, greetings, edits of the previous reply.
_NO_RETRIEVAL = re.compile(
    r"^\s*(hi|hello|hey|thanks|thank you|ok|okay|cool|great|bye)\b"
    r"|what can (you|we|i)\b|help me with\??\s*$|who are you|how do(es)? (you|this) work"
    r"|\b(make|keep) (it|that|this)\b|\b(shorter|longer|simpler|more concise)\b"
    r"|\b(rephrase|rewrite|reword|translate)\b",
    re.I,
)


# Turns that explicitly ask for her material always retrieve.
_WANTS_NOTES = re.compile(r"\b(my notes|the notes|my wiki|from class|in class|we learned|my (course|class)es?)\b", re.I)
_COURSES = {"Leading People": r"leading people", "Microeconomics": r"micro(economics)?\b",
            "Data and Decisions": r"data (and|&) decisions|\bd&d\b|statistics", "Marketing": r"marketing",
            "Finance": r"\bfinance|corporate finance", "Business Communication": r"business communication|buscomm"}


def _courses_in(message: str) -> list[str]:
    return [c for c, pattern in _COURSES.items() if re.search(pattern, message, re.I)]


def _course_outline(message: str) -> str:
    """Wiki page titles of the courses named in the message: a map of topics for plans and recaps."""
    import json
    man = config.INDEX_DIR / "manifest.json"
    if not man.exists():
        return ""
    notes = json.loads(man.read_text())["notes"].values()
    blocks = []
    for course, pattern in _COURSES.items():
        if re.search(pattern, message, re.I):
            titles = sorted(n["title"] for n in notes if n["course"] == course)
            if titles:
                blocks.append(f"Wiki pages for {course}: " + "; ".join(titles))
    return "\n".join(blocks)


# The assistant has no memory beyond the session; replies must not claim otherwise.
_FALSE_MEMORY = re.compile(r"\b(I've|I have|I'll|I will|I'm going to) (noted|note|saved|save|stored|store|"
                           r"remember|recorded|record|keep (a )?note)\b", re.I)
_MEMORY_FIX = ("\n\nIMPORTANT for this reply: do not say that you noted, saved, recorded or will remember "
               "anything. Say the information is kept only for this conversation and is not in her wiki, "
               "and suggest adding it to her notes in vault/raw/ and running `wiki ingest`.")


class ChatSession:
    def __init__(self):
        self.persona = (config.PROMPTS_DIR / "persona.md").read_text()
        self.history: list[dict] = []   # conversation context (user + assistant turns only)
        self.log: list[dict] = []

    def route(self, message: str) -> tuple[str, str, list[Hit]]:
        """Decide whether this turn retrieves notes. Returns (decision, reason, hits)."""
        if message.startswith("/notes "):
            q = message[len("/notes "):]
            return "retrieve", "forced by /notes", _get_index().search(q, config.TOP_K_CHAT)
        if _NO_RETRIEVAL.search(message):
            return "none", "conversational or editing turn", []
        if not Index.exists():
            return "none", "no index yet", []
        courses = _courses_in(message)
        hits = _get_index().search(message, config.TOP_K_CHAT * (6 if courses else 1))
        if courses:                                    # named course: keep its passages only
            hits = [h for h in hits if h.chunk.course in courses] or hits
        hits = hits[: config.TOP_K_CHAT]
        best = max((h.cosine for h in hits), default=0.0)
        if _WANTS_NOTES.search(message) or courses:
            return "retrieve", "message asks about her notes or names a course", hits
        if best >= config.CHAT_RETRIEVE_MIN_SIM:
            return "retrieve", f"best passage similarity {best:.2f} ≥ {config.CHAT_RETRIEVE_MIN_SIM}", hits
        return "none", f"best passage similarity {best:.2f} < {config.CHAT_RETRIEVE_MIN_SIM}", []

    def turn(self, message: str) -> dict:
        decision, reason, hits = self.route(message)
        text = message[len("/notes "):] if message.startswith("/notes ") else message
        user_content = text
        if hits:
            outline = _course_outline(text)
            user_content += ("\n\nNOTES from Luiza's wiki (cite as [N1], [N2]...; they are the only "
                             "verified facts about her courses):\n\n" + _evidence_block(hits, "N"))
            if outline:
                user_content += "\n\nTOPIC MAP (titles of her wiki pages):\n" + outline
        recent = self.history[-2 * config.CHAT_HISTORY_TURNS:]
        messages = [{"role": "system", "content": self.persona}, *recent,
                    {"role": "user", "content": user_content}]
        gen = llm.generate(messages, max_tokens=config.MAX_TOKENS_CHAT, temperature=0.3)
        guardrail = None
        if _FALSE_MEMORY.search(gen.text):            # harness guardrail: one rewrite without the false claim
            guardrail = "rewrote a reply that claimed to save or remember information"
            retry = [{"role": "system", "content": self.persona + _MEMORY_FIX}, *messages[1:]]
            gen = llm.generate(retry, max_tokens=config.MAX_TOKENS_CHAT, temperature=0.3)
        # History keeps the plain message: retrieved notes are per-turn context, not conversation.
        self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": gen.text}]
        entry = {"user": text, "retrieval": decision, "reason": reason,
                 "notes": [_hit_dict(h) for h in hits], "assistant": gen.text, "guardrail": guardrail,
                 "generation_seconds": gen.seconds, "mlx_peak_memory_gb": gen.peak_memory_gb}
        self.log.append(entry)
        return entry

    def reset(self):
        self.history.clear()

    def save(self) -> str | None:
        if not self.log:
            return None
        parts = [f"# Chat transcript\n\n- Model: `{config.LLM_MODEL}`, execution: **local**\n"]
        for i, e in enumerate(self.log, 1):
            notes = "".join(f"  - [N{j}] `{n['location']}`\n" for j, n in enumerate(e["notes"], 1))
            parts.append(
                f"\n## Turn {i}\n\n**User:** {e['user']}\n\n"
                f"_Retrieval: {e['retrieval']} ({e['reason']})_\n{notes}"
                + (f"_Guardrail: {e['guardrail']}_\n" if e.get("guardrail") else "") + "\n"
                f"**Assistant:** {e['assistant']}\n\n_{e['generation_seconds']} s_\n")
        record = {"mode": "chat", **llm.model_identity(), "turns": self.log}
        return evidence.save("chat", "session", record, "".join(parts))
