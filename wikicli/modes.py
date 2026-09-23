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


def ask(question: str, k: int = config.TOP_K_ASK, save: bool = True) -> dict:
    hits = _get_index().search(question, k)
    rules = (config.PROMPTS_DIR / "wiki-instructions.md").read_text()
    messages = [  # standalone: no chat history, no persona
        {"role": "system", "content": rules},
        {"role": "user", "content":
            f"Question: {question}\n\nEvidence passages:\n\n{_evidence_block(hits, 'S')}"},
    ]
    gen = llm.generate(messages, max_tokens=config.MAX_TOKENS_ASK)
    check = check_citations(gen.text, len(hits))
    result = {
        "mode": "ask", "question": question, **llm.model_identity(),
        "retrieved": [_hit_dict(h) for h in hits],
        "answer": gen.text,
        "citations": [{"id": f"S{n}", "location": hits[n - 1].chunk.location()} for n in check["valid"]],
        "citation_check": check,
        "timing": {"generation_seconds": gen.seconds, "prompt_tokens": gen.prompt_tokens,
                   "output_tokens": gen.output_tokens, "tokens_per_sec": gen.tokens_per_sec,
                   "mlx_peak_memory_gb": gen.peak_memory_gb, "process_peak_rss_gb": llm.process_rss_gb()},
    }
    if save:
        result["saved_to"] = evidence.save("ask", question, result, _ask_md(result))
    return result


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


def _ask_md(r: dict) -> str:
    cites = "\n".join(f"- [{c['id']}] `{c['location']}`" for c in r["citations"]) or "- none"
    t = r["timing"]
    return (
        f"# Ask: {r['question']}\n\n"
        f"- Model: `{r['model']}` ({r['quantization']}), runtime {r['runtime']}, execution: **{r['execution']}**\n"
        f"- Embeddings: `{r['embedding_model']}`\n"
        f"- Citation check: **{r['citation_check']['status']}**\n"
        f"- Generation: {t['generation_seconds']} s, {t['prompt_tokens']} prompt tokens, "
        f"{t['output_tokens']} output tokens, MLX peak memory {t['mlx_peak_memory_gb']} GB\n\n"
        f"## Answer\n\n{r['answer']}\n\n## Citations\n\n{cites}\n\n"
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
        # History keeps the plain message: retrieved notes are per-turn context, not conversation.
        self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": gen.text}]
        entry = {"user": text, "retrieval": decision, "reason": reason,
                 "notes": [_hit_dict(h) for h in hits], "assistant": gen.text,
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
                f"_Retrieval: {e['retrieval']} ({e['reason']})_\n{notes}\n"
                f"**Assistant:** {e['assistant']}\n\n_{e['generation_seconds']} s_\n")
        record = {"mode": "chat", **llm.model_identity(), "turns": self.log}
        return evidence.save("chat", "session", record, "".join(parts))
