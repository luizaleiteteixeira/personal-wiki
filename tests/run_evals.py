"""Run the four ask-mode evals and the chat/search mode checks, and save one report.

Usage:  .venv/bin/python -m tests.run_evals          (or: ./wiki-evals)

Expectations below mirror tests/test-plan.md and live outside the vault, so the
retriever can never find the answer key. The script records what happened; the
pass/fail judgement of each answer is written by a human in the evidence cards.
"""

import datetime as dt
import json
import platform
import subprocess
import time

from wikicli import config, llm
from wikicli.modes import ChatSession, ask, search

EVALS = [
    {"id": "T1", "kind": "direct, one source",
     "question": "What are the eight behaviors of a great manager identified by Google's Project Oxygen?",
     "expected_sources": ["raw/leading-people-midterm-study-guide.md"],
     "expected": "all eight behaviors, cited to the Leading People midterm study guide"},
    {"id": "T2", "kind": "paraphrased",
     "question": "What cheaper service did my former executive search firm create so that startups could afford to work with us?",
     "expected_sources": ["raw/micro-examples-in-the-wild-4.md"],
     "expected": "'strategic introductions': only the top five interviewed candidates, limited market mapping"},
    {"id": "T3", "kind": "two sources",
     "question": "What is a sunk cost, and how did I fall into the sunk cost trap at a restaurant?",
     "expected_sources": ["raw/micro-final-cheat-sheet.md", "raw/micro-examples-in-the-wild-1.md"],
     "expected": "definition (unrecoverable, irrelevant for decisions) + large pizza finished after 3 of 8 slices"},
    {"id": "T4", "kind": "unsupported",
     "question": "What WACC did I use in my Kellanova DCF valuation?",
     "expected_sources": [],
     "expected": "explicit insufficient-evidence response, no WACC number"},
]


def device() -> dict:
    def sysctl(key):
        return subprocess.run(["sysctl", "-n", key], capture_output=True, text=True).stdout.strip()
    return {"os": f"macOS {platform.mac_ver()[0]}", "chip": sysctl("machdep.cpu.brand_string"),
            "memory_gb": round(int(sysctl("hw.memsize")) / 2**30), "python": platform.python_version()}


def main():
    out_dir = config.RUNS_DIR / "evals" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"device": device(), **llm.model_identity(), "evals": [], "mode_checks": []}
    t_start = time.perf_counter()

    for e in EVALS:
        r = ask(e["question"])
        retrieved_paths = [p["path"] for p in r["retrieved"]]
        cited_paths = sorted({c["location"].split(" › ")[0] for c in r["citations"]})
        report["evals"].append({**e, "status": r["citation_check"]["status"], "answer": r["answer"],
                                "retrieved": [p["location"] for p in r["retrieved"]],
                                "expected_retrieved": all(s in retrieved_paths for s in e["expected_sources"]),
                                "cited_sources": cited_paths, "quotes": r["extracted_quotes"],
                                "weakly_supported": r["citation_check"]["weakly_supported"],
                                "timing": r["timing"], "card": r["saved_to"]})
        print(f"{e['id']}: {r['citation_check']['status']}  ({r['timing']['generation_seconds']} s)")

    # --- mode boundary checks
    chat = ChatSession()
    for msg in ["what can you help me with?", "what can we do?"]:
        t = chat.turn(msg)
        report["mode_checks"].append({"check": "chat capabilities", "input": msg, "retrieval": t["retrieval"],
                                      "reason": t["reason"], "output": t["assistant"]})
    chat.reset()
    t1 = chat.turn("Draft a short 5-day study plan for my Microeconomics final using my notes.")
    t2 = chat.turn("make that shorter")
    report["mode_checks"] += [
        {"check": "chat draft", "input": t1["user"], "retrieval": t1["retrieval"], "reason": t1["reason"],
         "notes": [n["location"] for n in t1["notes"]], "output": t1["assistant"]},
        {"check": "chat follow-up uses conversation", "input": t2["user"], "retrieval": t2["retrieval"],
         "reason": t2["reason"], "output": t2["assistant"]},
    ]
    chat.reset()
    t3 = chat.turn("For the record, my Kellanova WACC was 9%.")
    r = ask("What WACC did I use in my Kellanova DCF valuation?")
    report["mode_checks"] += [
        {"check": "claim made only in chat", "input": t3["user"], "output": t3["assistant"],
         "guardrail": t3["guardrail"]},
        {"check": "ask ignores chat history", "input": r["question"], "status": r["citation_check"]["status"],
         "output": r["answer"], "card": r["saved_to"]},
    ]
    s = search("price discrimination")
    report["mode_checks"].append({"check": "search returns passages only", "input": s["query"],
                                  "passages": [p["location"] for p in s["passages"]], "card": s["saved_to"]})
    report["chat_transcript"] = chat.save()
    report["total_seconds"] = round(time.perf_counter() - t_start, 1)
    report["process_peak_rss_gb"] = llm.process_rss_gb()

    (out_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    (out_dir / "report.md").write_text(render(report), encoding="utf-8")
    print(f"report: {(out_dir / 'report.md').relative_to(config.ROOT)}")


def render(r: dict) -> str:
    d = r["device"]
    lines = [f"# Eval report\n",
             f"- Device: {d['chip']}, {d['memory_gb']} GB unified memory, {d['os']}",
             f"- Model: `{r['model']}` ({r['quantization']}), {r['runtime']}, execution **{r['execution']}**",
             f"- Embeddings: `{r['embedding_model']}`",
             f"- Total run time: {r['total_seconds']} s, process peak memory {r['process_peak_rss_gb']} GB\n",
             "## Ask-mode evals\n",
             "| Test | Kind | Status | Expected source retrieved | Cited sources | Time (s) |",
             "|---|---|---|---|---|---|"]
    for e in r["evals"]:
        lines.append(f"| {e['id']} | {e['kind']} | {e['status']} | {'yes' if e['expected_retrieved'] else 'NO'}"
                     f" | {', '.join(e['cited_sources']) or '-'} | {e['timing']['generation_seconds']} |")
    for e in r["evals"]:
        quotes = "\n".join(f"- [{q['id']}] `{q['location']}`: \"{q['text']}\"" for q in e["quotes"]) or "- none"
        weak = "; ".join(w["sentence"] for w in e["weakly_supported"]) or "none"
        lines += [f"\n### {e['id']}: {e['question']}\n", f"Expected: {e['expected']}\n",
                  f"Verified quotes (step 1):\n{quotes}\n", f"Weakly supported sentences: {weak}\n",
                  f"Answer:\n\n> " + e["answer"].replace("\n", "\n> "), f"\nFull evidence card: `{e['card']}`"]
    lines.append("\n## Mode checks\n")
    for c in r["mode_checks"]:
        lines.append(f"### {c['check']}\n\nInput: `{c['input']}`")
        if "retrieval" in c:
            lines.append(f"\nRetrieval decision: **{c['retrieval']}** ({c['reason']})")
        if c.get("notes"):
            lines.append("\nNotes used: " + "; ".join(f"`{n}`" for n in c["notes"]))
        if "passages" in c:
            lines.append("\nPassages returned (no generated answer):\n" + "\n".join(f"- `{p}`" for p in c["passages"]))
        if c.get("guardrail"):
            lines.append(f"\nHarness guardrail: {c['guardrail']}")
        if "output" in c:
            lines.append("\nOutput:\n\n> " + c["output"].replace("\n", "\n> "))
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
