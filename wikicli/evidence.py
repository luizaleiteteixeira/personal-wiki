"""Saved outputs: every ask/search/chat/ingest run is written to runs/ as JSON + Markdown,
so results can be inspected later without rerunning the model."""

import datetime as dt
import json
import re

from . import config


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "run"


def save(mode: str, title: str, record: dict, markdown: str) -> str:
    folder = config.RUNS_DIR / mode
    folder.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base = folder / f"{stamp}-{_slug(title)}"
    record = {"saved_at": dt.datetime.now().isoformat(timespec="seconds"), **record}
    base.with_suffix(".json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
    base.with_suffix(".md").write_text(markdown, encoding="utf-8")
    return str(base.relative_to(config.ROOT)) + ".md"


def passages_md(hits: list[dict], label: str) -> str:
    out = []
    for i, h in enumerate(hits, 1):
        quoted = "\n".join("> " + l for l in h["text"].splitlines())
        out.append(f"**[{label}{i}]** `{h['location']}`  (fused score {h['score']:.4f}, "
                   f"cosine {h['cosine']:.3f}, bm25 {h['bm25']:.2f})\n\n{quoted}\n")
    return "\n".join(out)
