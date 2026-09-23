"""`wiki` command line: parses the command, picks the mode, prints results, reports errors."""

import argparse
import sys
import textwrap
from pathlib import Path

from . import config

BOLD, DIM, CYAN, YELLOW, RESET = ("\033[1m", "\033[2m", "\033[36m", "\033[33m", "\033[0m") \
    if sys.stdout.isatty() else ("",) * 5

EPILOG = f"""\
examples:
  wiki ingest                         read vault/raw/, rebuild the index, write wiki pages
  wiki ingest vault/raw/micro-final-cheat-sheet.md   (re)ingest one source
  wiki search "price discrimination"  show original passages (no model needed)
  wiki ask "What is a sunk cost?"     cited answer from your notes, or "insufficient evidence"
  wiki chat                           talk to the study-buddy assistant
  wiki status                         show model, index and wiki counts

configuration:
  model       {config.LLM_MODEL}   (override with WIKI_LLM)
  embeddings  {config.EMBED_MODEL}   (override with WIKI_EMBED)
  sources     vault/raw/      wiki pages  vault/wiki/      landing page  vault/index.md
  index       index/          saved runs  runs/            prompts       prompts/
  execution   local only (--mode local is the default; there is no online mode)
"""


def _wrap(text: str, indent: str = "  ") -> str:
    return "\n".join(textwrap.fill(p, 100, initial_indent=indent, subsequent_indent=indent)
                     if p.strip() else "" for p in text.splitlines())


def _check_mode(mode: str):
    if mode != "local":
        raise SystemExit(f"error: mode '{mode}' is not available. This project runs Gemma locally only "
                         "(use --mode local).")


# ---------------------------------------------------------------- commands

def cmd_ingest(args):
    from .ingest import ingest
    target = Path(args.path).resolve() if args.path else None
    if target and not target.exists():
        raise SystemExit(f"error: {args.path} does not exist")
    if target and config.RAW_DIR.resolve() not in [target, *target.parents]:
        raise SystemExit("error: sources must live in vault/raw/ (originals are kept there unchanged)")
    print(f"{BOLD}Ingesting{RESET} {target or config.RAW_DIR} with {config.LLM_MODEL} (local)")
    stats = ingest(target, force=args.force, skip_notes=args.skip_notes,
                   log=lambda s: print(DIM + s + RESET))
    from . import evidence
    md = "# Ingest run\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in stats.items()) + "\n"
    saved = evidence.save("ingest", "ingest", stats, md)
    print(f"\n{BOLD}Done{RESET} in {stats['seconds_total']} s: {stats['passages_indexed']} passages indexed, "
          f"{stats['notes_generated_or_updated']} notes written/updated, "
          f"{stats['sections_unchanged_skipped']} unchanged sections skipped, "
          f"{stats['wiki_notes_total']} wiki notes in total. Peak memory {stats['peak_process_memory_gb']} GB.")
    print(f"{DIM}saved {saved}{RESET}")


def cmd_search(args):
    from .modes import search
    r = search(" ".join(args.query), k=args.k, keyword_only=args.keyword)
    print(f"{BOLD}Search{RESET} ({r['method']}): {r['query']}\n")
    if not r["passages"]:
        print("  No matching passages.")
    for i, p in enumerate(r["passages"], 1):
        print(f"{CYAN}[P{i}] {p['location']}{RESET}  {DIM}cos {p['cosine']:.2f} · bm25 {p['bm25']:.1f}{RESET}")
        print(_wrap(p["text"][:700] + ("…" if len(p["text"]) > 700 else "")) + "\n")
    print(f"{DIM}saved {r['saved_to']}{RESET}")


def cmd_ask(args):
    _check_mode(args.mode)
    from .modes import ask
    r = ask(" ".join(args.question), k=args.k)
    print(f"{BOLD}Ask{RESET} · {r['model']} · {r['execution']}\n")
    print(_wrap(r["answer"]) + "\n")
    print(f"{BOLD}Citations{RESET} ({r['citation_check']['status']})")
    for c in r["citations"]:
        print(f"  [{c['id']}] {c['location']}")
    if r["citation_check"]["invalid"]:
        print(f"{YELLOW}  warning: cited passages that were not retrieved: "
              f"{', '.join('S%d' % n for n in r['citation_check']['invalid'])}{RESET}")
    if r["citation_check"]["status"] == "uncited_answer":
        print(f"{YELLOW}  warning: the answer has no citations; treat it as unsupported.{RESET}")
    for w in r["citation_check"]["weakly_supported"]:
        print(f"{YELLOW}  check: \"{w['sentence'][:90]}\" shares only {int(w['overlap'] * 100)}% of its words "
              f"with {', '.join(w['cited'])}{RESET}")
    print(f"\n{BOLD}Verified quotes{RESET} (step 1, checked against the passages)")
    for q in r["extracted_quotes"]:
        print(f"  [{q['id']}] \"{q['text'][:110]}{'…' if len(q['text']) > 110 else ''}\"")
    if not r["extracted_quotes"]:
        print("  none: the harness answered 'insufficient evidence' without a second model call")
    if r["rejected_quotes"]:
        print(f"{DIM}  rejected {len(r['rejected_quotes'])} quote(s) not found verbatim in the passages{RESET}")
    if args.show_evidence:
        print(f"\n{BOLD}Retrieved passages{RESET}")
        for i, p in enumerate(r["retrieved"], 1):
            print(f"{CYAN}[S{i}] {p['location']}{RESET}\n" + _wrap(p["text"][:500]) + "\n")
    t = r["timing"]
    print(f"\n{DIM}{t['generation_seconds']} s · {t['tokens_per_sec']} tok/s · MLX peak {t['mlx_peak_memory_gb']} GB"
          f" · saved {r['saved_to']}{RESET}")


def cmd_chat(args):
    _check_mode(args.mode)
    from .modes import ChatSession
    session = ChatSession()
    print(f"{BOLD}Oski Notes{RESET} · {config.LLM_MODEL} · local")
    print(f"{DIM}Commands: /notes <question> forces a notes lookup · /reset clears the conversation · "
          f"/quit exits{RESET}\n")
    try:
        while True:
            try:
                msg = input(f"{BOLD}you ›{RESET} ").strip()
            except EOFError:
                break
            if not sys.stdin.isatty():      # scripted demo: show what was "typed"
                print(msg)
            if not msg:
                continue
            if msg in {"/quit", "/exit", "quit", "exit"}:
                break
            if msg == "/reset":
                session.reset()
                print(f"{DIM}(conversation cleared){RESET}\n")
                continue
            e = session.turn(msg)
            tag = f"looked up {len(e['notes'])} note passages" if e["notes"] else "no notes lookup"
            print(f"{DIM}({tag}: {e['reason']}){RESET}")
            if e["guardrail"]:
                print(f"{DIM}(guardrail: {e['guardrail']}){RESET}")
            print(f"{CYAN}oski ›{RESET} " + e["assistant"].strip() + "\n")
            for j, n in enumerate(e["notes"], 1):
                if f"[N{j}]" in e["assistant"]:
                    print(f"{DIM}  [N{j}] {n['location']}{RESET}")
            if e["notes"]:
                print()
    except KeyboardInterrupt:
        print()
    saved = session.save()
    if saved:
        print(f"{DIM}transcript saved to {saved}{RESET}")


def cmd_status(args):
    import json
    from .retrieval import CHUNKS_FILE
    print(f"model       {config.LLM_MODEL}\nembeddings  {config.EMBED_MODEL}")
    raw = [p.name for p in sorted(config.RAW_DIR.iterdir()) if p.is_file()] if config.RAW_DIR.exists() else []
    print(f"sources     {len(raw)} files in vault/raw/")
    n_chunks = sum(1 for _ in CHUNKS_FILE.open()) if CHUNKS_FILE.exists() else 0
    print(f"index       {n_chunks} passages" if n_chunks else "index       not built (run `wiki ingest`)")
    notes = list(config.WIKI_DIR.rglob("*.md")) if config.WIKI_DIR.exists() else []
    print(f"wiki        {len(notes)} notes in vault/wiki/")
    man = config.INDEX_DIR / "manifest.json"
    if man.exists():
        m = json.loads(man.read_text())
        print(f"manifest    {len(m['sections'])} source sections mapped to {len(m['notes'])} notes")


# ---------------------------------------------------------------- parser

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wiki",
        description="Personal MBA wiki: local Gemma + retrieval over your own notes, fully offline.",
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", metavar="<command>")

    s = sub.add_parser("ingest", help="index sources and generate linked wiki pages with Gemma")
    s.add_argument("path", nargs="?", help="a file or folder inside vault/raw/ (default: all of vault/raw/)")
    s.add_argument("--force", action="store_true", help="regenerate pages even for unchanged sections")
    s.add_argument("--skip-notes", action="store_true", help="only rebuild the search index (no Gemma)")
    s.set_defaults(func=cmd_ingest)

    s = sub.add_parser("search", help="show original passages and their locations (no answer generated)")
    s.add_argument("query", nargs="+")
    s.add_argument("-k", type=int, default=config.TOP_K_SEARCH, help="number of passages (default %(default)s)")
    s.add_argument("--keyword", action="store_true", help="BM25 keyword search only (no embedding model)")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("ask", help="standalone factual answer with citations, or 'insufficient evidence'")
    s.add_argument("question", nargs="+")
    s.add_argument("--mode", default="local", help="execution mode (only 'local' is available)")
    s.add_argument("-k", type=int, default=config.TOP_K_ASK, help="passages given to Gemma (default %(default)s)")
    s.add_argument("--show-evidence", action="store_true", help="print the retrieved passages")
    s.set_defaults(func=cmd_ask)

    s = sub.add_parser("chat", help="personal study assistant with conversation memory")
    s.add_argument("--mode", default="local", help="execution mode (only 'local' is available)")
    s.set_defaults(func=cmd_chat)

    s = sub.add_parser("status", help="show model, index and wiki counts")
    s.set_defaults(func=cmd_status)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    from .llm import ModelUnavailable
    try:
        args.func(args)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except ModelUnavailable as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0
