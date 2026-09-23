# Personal MBA Wiki: Local Gemma + RAG

A command-line assistant that answers questions about **my own Berkeley Haas MBA notes**, running
entirely on my laptop with a local open-weight Gemma model. It turns 16 original notes into a linked
Obsidian wiki (92 pages), and offers three modes:

| Mode | What it does | Uses the model? |
|---|---|---|
| `wiki chat` | Study-buddy assistant with a personality and conversation memory; looks up notes only when a turn needs them | yes |
| `wiki ask` | Standalone factual answer with citations, or an explicit *insufficient evidence* reply | yes |
| `wiki search` | Returns original passages and their locations, with no generated answer | no |

Plus `wiki ingest` (build the index and wiki pages), `wiki status` and `wiki --help`.

> **Evidence at a glance**
> Offline demo recording: [`evidence/offline-demo.gif`](evidence/offline-demo.gif) ·
> Eval report: [`evidence/eval-report.md`](evidence/eval-report.md) ·
> Ask-mode evidence cards: [`evidence/ask-evidence-cards.md`](evidence/ask-evidence-cards.md) ·
> Obsidian screenshots: [`evidence/screenshots/`](evidence/screenshots/) ·
> Test plan written before building: [`tests/test-plan.md`](tests/test-plan.md)

---

## 1. Purpose and sources

**What the wiki is for.** Reviewing my first-year MBA courses: definitions, frameworks, formulas,
case takeaways, and my own "Examples in the Wild" write-ups, with answers I can trace back to my notes.

**Sources** (`vault/raw/`, 16 files, about 19,000 words plus a 35-page PDF). All of them are my own
notes or write-ups, exported from my Google Drive. The full catalog, with original titles, Drive file
IDs and export notes, is in [`sources.csv`](sources.csv).

| Course | Sources |
|---|---|
| Leading People | Final exam study guide, midterm study guide |
| Microeconomics | Final cheat sheet, "Examples in the Wild" 1-5 |
| Data and Decisions | Cheat sheet |
| Marketing | Final cheat sheet (the second tab, "Perplexity", was drafted with an AI tool), Nike case write-up |
| Finance | Finance summary (PDF, kept as the original file) |
| Business Communication | Case write-ups 1-4 |

**Deliberately excluded:** grading sheets and student data from my GSI role (FERPA), exams and
answer keys, textbooks, handwritten `.note` files (no extractable text), and personal reflections.
Classmates' names were replaced with "the two second-years"; this edit is recorded in `sources.csv`.

**How originals connect to wiki pages.** `wiki ingest` splits each original into sections by its own
headings (Markdown headings, ALL-CAPS cheat-sheet headings, or "Lecture N" in the PDF). Gemma writes one
page per section; pages about the same subject are merged. Every page lists its sources in the front
matter (`sources`, `source_ids`) and links back to the original file (and PDF page) under **Sources**.
The originals in `raw/` are never modified by the program.

## 2. Setup and device

| | |
|---|---|
| Device | MacBook, Apple M4, 16 GB unified memory (CPU and GPU share it), macOS 15.7.4 |
| Free disk | 24 GB after downloads (models use about 9.6 GB) |
| Runtime | [MLX](https://github.com/ml-explore/mlx) 0.32.2 via `mlx-vlm` 0.7.2, Python 3.12 |
| Language model | `mlx-community/gemma-4-e4b-it-4bit`: Gemma 4 E4B instruction-tuned, 4-bit MLX quantization |
| Embedding model | `mlx-community/all-MiniLM-L6-v2-4bit` (384-dim, 26 MB), local |
| Other | `pypdf` 6.19.0 (PDF text), `numpy` |

### Install (online, once)

```bash
brew install uv                                   # Python package manager
git clone https://github.com/luizaleiteteixeira/personal-wiki.git && cd personal-wiki
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
# download the models into the local Hugging Face cache (about 9.6 GB)
.venv/bin/python -c "from huggingface_hub import snapshot_download as d; \
d('mlx-community/gemma-4-e4b-it-4bit'); d('mlx-community/all-MiniLM-L6-v2-4bit')"
```

Model weights are **not** committed. Official source: the Gemma 4 E4B instruction-tuned weights,
converted to MLX by the `mlx-community` organization on Hugging Face (identifier above).

### Run (works offline)

```bash
./wiki --help
./wiki ingest                                   # index vault/raw/ and write the wiki (about 16 min the first time)
./wiki ingest vault/raw/micro-examples-in-the-wild-1.md   # re-ingest a single source
./wiki search "price discrimination"
./wiki ask "What is a sunk cost, and how did I fall into the sunk cost trap at a restaurant?"
./wiki chat
.venv/bin/python -m tests.run_evals             # run all four evals plus the mode checks
```

The `wiki` launcher sets `HF_HUB_OFFLINE=1`, so models are only read from the local cache and no
network call is ever attempted. Open **`vault/`** (not the repository) as the Obsidian vault.

### Why Gemma 4 E4B (4-bit), and measured cost

I started with **E2B** (the classroom default for tight memory) and compared it with **E4B** on the
same four evals ([attempts](runs/ask/)):

| | E2B 4-bit | E4B 4-bit (chosen) |
|---|---|---|
| MLX peak memory during an answer | 4.3 GB | **5.9 GB** |
| Answer time (ask mode, about 1,100-1,600 prompt tokens) | about 3 s (60 tokens/s) | **5-7 s** (34 tokens/s) |
| T2 (paraphrased question) | used the wrong passage | used the right passage (partial: see §5) |
| T1, T3, T4 | pass | pass |

E4B fits comfortably in 16 GB alongside other apps and is the smallest model that picked the
right evidence on the paraphrased test, so I kept it. The 26B MoE was not considered: it needs
about 14.4 GB just to load, which leaves no headroom on a 16 GB machine.

**Measured on this device (E4B):**
- Full ingestion of 16 sources: 103 sections, 266 passages, **947 s** (9.1 s per wiki page).
  Re-ingesting unchanged sources takes about 20 s (sections are skipped by content hash).
- Single-source re-ingest: 11.6 s.
- Ask (two model calls: extract, then answer): **8-10 s** per answer; an unsupported question stops
  after the first call (**3.9 s**). MLX peak memory **5.9 GB**, process resident memory 3.1 GB.
- Search: under 1 s, no language model loaded.

## 3. Architecture

```
            ┌──────────── CLI (wikicli/cli.py): parses the command, prints results, reports errors
            │
            ▼
  ┌─────────────────── HARNESS (wikicli/modes.py, ingest.py) ───────────────────┐
  │ picks the mode · loads instructions · manages conversation · decides whether │
  │ to retrieve · builds prompts · calls Gemma · checks citations · saves runs    │
  └───────┬───────────────────────────────┬───────────────────────────┬─────────┘
          ▼                               ▼                           ▼
  RETRIEVAL TOOL (retrieval.py)     MODEL (llm.py)              SAVED OUTPUTS (evidence.py)
  BM25 + MiniLM embeddings,         Gemma 4 E4B via MLX,        runs/<mode>/*.json + *.md
  fused with RRF; returns           sees only the messages
  passages with path/section/page   the harness gives it
```

- **Model**: generates text from the messages the harness assembles. It does not read files, remember
  past sessions, or call tools.
- **Retrieval tool**: `index/chunks.jsonl` (266 passages, about 900 characters each, split on line
  boundaries so bullets and formulas stay whole) plus `index/embeddings.npy`. A query is scored by BM25
  (keywords) and by cosine similarity (meaning); the two rankings are combined with reciprocal rank
  fusion. `wiki search` exposes this tool directly.
- **RAG workflow** (ask): question → retrieve 6 passages → **Gemma quotes the evidence verbatim** →
  harness verifies every quote against its passage → **Gemma answers from verified quotes only** →
  citation and support checks → display and save.
- **Harness**: everything around the model. The core logic is in `wikicli/modes.py` (about 310 lines).

**One path through the code: `./wiki ask "What is a sunk cost…?"`**
1. `cli.py:cmd_ask` rejects any mode other than `local`, then calls `modes.ask`.
2. `modes.ask` loads the index and calls `Index.search` (`retrieval.py`), which returns 6 hits. Here
   they are the Examples in the Wild 1 essay and the "Costs" section of the Micro cheat sheet.
3. **Extract.** It builds a **fresh** message list with `prompts/extract-instructions.md` and the question
   plus the numbered passages; no chat history and no persona are included. `llm.generate` applies
   Gemma's chat template and runs MLX generation at temperature 0. Gemma returns lines such as
   `[S3] "Sunk = cannot be recovered, irrelevant for decisions"`.
4. **Verify.** `verify_quotes` keeps a quote only if it occurs in the passage it names (exactly, or with
   at least 90% of its characters matching in order). If no quote survives, the harness returns
   "Insufficient evidence" without calling the model again.
5. **Answer.** A second fresh call with `prompts/wiki-instructions.md` and only the verified quotes.
6. **Check.** `check_citations` parses `[S#]`, flags passages that were not retrieved, and labels the
   result (`answered_with_citations`, `insufficient_evidence`, `uncited_answer`, `invalid_citation`).
   `support_check` flags cited sentences whose content words mostly do not appear in the cited passage.
7. `evidence.save` writes `runs/ask/<time>-<question>.json` and `.md` (question, model identity,
   retrieved passages with scores, verified and rejected quotes, answer, citations, checks, timing,
   memory), and the CLI prints the answer, citations and quotes.

**Chat**: system = `prompts/persona.md` (voice plus an accurate list of what it can and cannot do); the
last 6 exchanges are kept as conversation context. **Retrieval decision** (`ChatSession.route`):
- no lookup for capability questions, greetings, and edits of the previous reply ("make that shorter");
- lookup when the message asks for her notes or names a course (retrieval is then limited to that
  course, and the list of that course's wiki pages is added as a topic map);
- otherwise, lookup only if the best passage has cosine similarity ≥ 0.40.

Retrieved notes are cited as `[N#]`. They are added to that turn only, while the history keeps just the
plain messages. Chat never feeds `ask`: each ask call starts from an empty context.
**Guardrail:** the model has no memory beyond the session, so if a reply claims "I've noted / saved / will
remember…", the harness regenerates it once with an explicit instruction, and logs that it did.

**Errors**: missing index → "Run `wiki ingest` first"; model not in the cache → message with the
download command (exit code 2); sources outside `vault/raw/` are refused; `--mode online` is refused.

## 4. Design choices

- **Passage size**: about 900 characters (roughly 200 tokens). Six passages plus rules come to about
  1,100-1,600 prompt tokens per ask, far below Gemma's context window. That keeps answers fast and
  focused, so the whole wiki is never sent.
- **Hybrid retrieval**: BM25 alone would miss paraphrases (test 2 avoids the source's keywords);
  embeddings alone blur exact terms like "WACC" or "Project Oxygen". RRF is simple and needs no tuning.
- **Research rules vs. personality**: kept in separate files and loaded per mode
  (`prompts/extract-instructions.md` and `prompts/wiki-instructions.md` for ask, `prompts/persona.md` for chat, `prompts/ingest-instructions.md`
  for page generation).
- **Wiki naming and folders**: Gemma proposes a 2-5 word subject title (such as "Price Discrimination
  Strategies" or "Sunk Cost Reasoning Example"); generic titles are rejected. Pages live in one folder
  per course, `wiki/<Course>/<Title>.md`, and the first heading matches the file name. Machine IDs
  (`source_ids`, such as `micro-final-cheat-sheet#costs`) are kept in front matter, never in file names.
  If two courses produce the same title, the second gets a qualifier (for example, "Pricing - Marketing").
- **Merging duplicates**: the Marketing cheat sheet summarizes several cases twice. Same-course page
  pairs with similar title and summary (cosine ≥ 0.70) are shown to Gemma, which answers whether they
  are the same subject. 9 pairs were merged (101 → 92 pages). Gemma kept "Monopolistic Competition" and
  "Oligopoly" apart, which embeddings alone could not.
- **Meaningful links**: each page gets up to 3 related pages. Embeddings propose neighbours, and Gemma
  writes one sentence on why the link matters (for example, *Sunk Cost Reasoning Example →
  Economic Cost Concepts: "Contrasts the emotional trap of sunk costs with the rational framework of
  economic cost"*). Explanations are cached.
- **Re-ingestion without duplicates**: `index/manifest.json` maps every source section (by ID and
  content hash) to its page. Unchanged sections are skipped; changed ones rewrite the *same* file;
  passages of a re-ingested source replace its old passages in the index. I verified this by
  force-re-ingesting one source: same 92 files before and after. Pages marked `reviewed: true` are never
  overwritten, so manual corrections survive. Hand-written pages are never deleted.
- **Model settings**: temperature 0 for ask and ingest (reproducible), 0.3 for chat.

## 5. Evidence

The evals were designed before building ([`tests/test-plan.md`](tests/test-plan.md)); the answer key
lives outside the vault so the retriever cannot find it.

| Test | Question | Expected source | Retrieved? | Result |
|---|---|---|---|---|
| T1 | eight behaviors of Google's Project Oxygen | Leading People midterm guide | rank 1 | ✅ all eight, cited |
| T2 | cheaper service my former executive search firm created for startups (paraphrased) | Examples in the Wild 4 | rank 1 | ⚠️ partial: right passage, but "strategic introductions" is not named |
| T3 | sunk cost + my restaurant example (two sources) | Micro cheat sheet + Examples 1 | ranks 1-3 | ✅ definition and story; every sentence restates a verified quote |
| T4 | the WACC in my Kellanova DCF (not in the wiki) | none | general WACC passages only | ✅ no quote could be verified, so the harness refused; no number |

Full cards with retrieved passages, answers, citations and my assessment:
[`evidence/ask-evidence-cards.md`](evidence/ask-evidence-cards.md). Mode checks (chat capabilities,
follow-up, chat claim not used by ask, raw search): [`evidence/eval-report.md`](evidence/eval-report.md).
Offline run: [`evidence/offline-demo.gif`](evidence/offline-demo.gif) (asciinema recording
[`evidence/offline-demo.cast`](evidence/offline-demo.cast)).

**Before/after.** The first offline evaluation used a single-step ask. Its cards, report and recording
are kept in [`evidence/previous/`](evidence/previous/). Earlier model and prompt attempts are in
[`runs/ask/`](runs/ask/) (`attempt-1` … `attempt-3-*`).

| | v1: single step | v2: extract → verify → answer (current) |
|---|---|---|
| T1 | ✅ | ✅ |
| T2 | ⚠️ right passage, service not named | ⚠️ same, and the first sentence blends Examples 3 into "a service" |
| T3 | ✅, with some unquoted (true) details | ✅, every sentence traceable to a verified quote |
| T4 | ✅ model chose to refuse | ✅ refusal enforced by the harness (no second call) |
| Chat "save a fact" | ⚠️ said "I've noted that" and invented "no Finance section" | ✅ guardrail rewrote it: kept for this conversation only, not in the wiki |

### Obsidian: the wiki as a human sees it

Open `vault/` as the Obsidian vault and start at `index.md`.

| Screenshot | What it shows |
|---|---|
| [1 · Open note](evidence/screenshots/1-open-note-properties.webp) | *Sunk Cost Reasoning Example*: short descriptive file name, matching heading, front matter with `sources` / `source_ids` (machine IDs stay in metadata) |
| [2 · Page list](evidence/screenshots/2-page-list.png) | `wiki/` organized in one folder per course; readable page names |
| [3 · Graph](evidence/screenshots/3-graph.webp) | Graph view filtered with `path:wiki/` (attachments and orphans hidden), readable labels, links between related subjects across courses |
| [4 · Note → source](evidence/screenshots/4-note-to-source-trace.webp) | Left: the note's *Related notes* (each with a reason) and *Sources*. Right: the original essay in `raw/`, which the note summarizes |
| [5 · Related note → source](evidence/screenshots/5-related-note-to-source-trace.webp) | Left: the related note *Economic Cost Concepts*. Right: its original, the "Costs" section of the Micro cheat sheet ("Sunk = cannot be recovered, irrelevant for decisions") |

**Trace of one note to its evidence:** *Sunk Cost Reasoning Example* → (related note, "Contrasts sunk
costs with economic cost…") → *Economic Cost Concepts* → `raw/micro-final-cheat-sheet.md › Costs`, and
directly → `raw/micro-examples-in-the-wild-1.md`. These are exactly the two passages that ask-mode
test T3 retrieves and cites. The source catalog for all originals is [`sources.csv`](sources.csv).

## 6. Reflection: a real failure and what I would change

**Failure (T2).** The question describes my former employer as "my former executive search firm" and
never says "Egon Zehnder", "versioning" or "second-degree price discrimination".
- **Retrieval handled it**: the right passage ranked first thanks to the embedding half of the hybrid
  search.
- **Generation was the weak link**:
  - With E2B and my first rules, the model replied *insufficient evidence*, apparently because the
    passage never uses the phrase "executive search firm".
  - Loosening the rules made E2B answer from the neighbouring essay (Examples 3, about segment
    pricing) instead.
  - E4B picks the right passage, but it summarizes it as "a lower-priced version of its service" and
    blends in the third-degree pricing story from Examples 3.
- **Root cause**: two very similar passages from the same series appear together, and a small model
  merges them instead of quoting the specific name.

**Improvement I tried: extract → verify → answer.** Gemma first copies the sentences that answer the
question, the harness checks that each quote really exists in its passage, and Gemma then answers from
the verified quotes only. I reran all four evals offline (cards and recording in `evidence/`).
- **What improved**:
  - Every claim in T1 and T3 now traces to a verified quote.
  - T4's refusal is enforced by code: no quote survives, so the model is never asked to answer.
  - Invented quotes are rejected automatically.
- **What stayed wrong**: T2. Step 1 quoted the Examples 4 sentence about "the lower-priced version", but
  not the sentence that names it ("strategic introductions"). The answer still blends it with Examples
  3. I also tried a general rule ("when a sentence refers to something by description, also quote the
  sentence that names it"). The output was identical at temperature 0, so I removed it. I stopped
  there on purpose: tuning prompts until this one question passes would overfit the test.
- **What I learned about my checks**: the new word-overlap support check flagged nothing in T2, because
  every word of the blended sentence does appear in the cited passages. It catches invented content,
  not a wrong connection between true facts.

**Next improvement to try.** Rerank before generating: score each retrieved passage against the question
with a small local cross-encoder, and pass only passages from the single best-matching source when one
clearly dominates. That would remove the competing Examples 3 passage from T2's context. Alternatively,
add an entailment check on each sentence (does the quote *imply* the claim?) instead of word overlap.

**Other known limitations.**
- Two merges are debatable ("Rebranding" into "Promotion and Communications", "Differentiation" into
  "Brand Strategy").
- 10 pages have no related-page links, and are reachable only from `index.md`.
- Diagrams in the cheat sheets were not exported, so their content is missing.
- The chat guardrail is a pattern match. It catches "I've noted / saved / will remember", but not every
  possible phrasing.
