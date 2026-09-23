# Ask-mode evidence cards (offline run)

**Run:** 2026-09-22, 18:21-18:23 PDT, recorded in [`offline-demo.cast`](offline-demo.cast) /
[`offline-demo.gif`](offline-demo.gif). The recording starts by showing `Wi-Fi Power (en0): Off`
and a failed request to huggingface.co. Every command is a new CLI process.

**Model:** `mlx-community/gemma-4-e4b-it-4bit` (Gemma 4 E4B, instruction-tuned, 4-bit MLX), runtime
mlx-vlm 0.7.2 / mlx 0.32.2, execution **local**, temperature 0.
**Retrieval:** hybrid BM25 + `mlx-community/all-MiniLM-L6-v2-4bit` embeddings (RRF), top 6 passages.
**Device:** Apple M4, 16 GB unified memory, macOS 15.7.4.

Expectations were written before building, in [`../tests/test-plan.md`](../tests/test-plan.md).
Each card links to the full saved run (all retrieved passage texts and scores).
The assessments are mine, made by opening each cited passage.

---

## T1: direct question, one source

**Question:** What are the eight behaviors of a great manager identified by Google's Project Oxygen?

**Expected source:** `raw/leading-people-midterm-study-guide.md › Managing People`

**Retrieved passages** (the expected one is ranked first):

| # | Location | cosine | BM25 |
|---|---|---|---|
| S1 | `raw/leading-people-midterm-study-guide.md › Managing People` | 0.67 | 21.2 |
| S2 | `raw/leading-people-midterm-study-guide.md › Introduction: Leadership vs. Management` | 0.43 | 8.8 |
| S3 | `raw/micro-examples-in-the-wild-2.md › Examples in the Wild 2` | 0.40 | 4.1 |
| S4 | `raw/leading-people-final-study-guide.md › Macro Interactions — Change` | 0.39 | 3.7 |
| S5 | `raw/marketing-final-cheat-sheet.md › Module 2: Market Research & Consumer Insights` | 0.38 | 3.7 |
| S6 | `raw/leading-people-final-study-guide.md › Complex Interactions — Persuasion` | 0.32 | 5.5 |

**Gemma's answer** (6.4 s, MLX peak 5.86 GB):
> The eight behaviors of a great manager, according to Google’s Project Oxygen, are:
> 1. Good coach [S1]. 2. Empowers (does not micromanage) [S1]. 3. Cares about people [S1].
> 4. Is results-oriented [S1]. 5. Is a good communicator [S1]. 6. Supports careers [S1].
> 7. Has a clear vision/strategy [S1]. 8. Possesses technical expertise [S1].

**Citation check:** `answered_with_citations`; all claims cite S1.

**Assessment: ✅ Pass.** All eight behaviors match the source line *"Good coach; empowers (no
micromanage); cares about people; results-oriented; good communicator; supports careers; clear
vision/strategy; technical expertise."* Nothing was added.

Full run: [`runs/ask/20260922-182137-…`](../runs/ask/20260922-182137-what-are-the-eight-behaviors-of-a-great-manager-id.md)

---

## T2: answerable question, phrased differently from the source

**Question:** What cheaper service did my former executive search firm create so that startups could afford to work with us?

**Expected source:** `raw/micro-examples-in-the-wild-4.md`: *"we created a new product: 'strategic
introductions.' In this model, we presented only the top five candidates we had interviewed and
limited the level of market mapping."*

**Retrieved passages** (the expected one is ranked first, even though the question shares none of its key terms):

| # | Location | cosine | BM25 |
|---|---|---|---|
| S1 | `raw/micro-examples-in-the-wild-4.md › Examples in the Wild 4` | 0.50 | 27.5 |
| S2 | `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3` | 0.52 | 14.6 |
| S3 | `raw/micro-examples-in-the-wild-2.md › Examples in the Wild 2` | 0.46 | 22.0 |
| S4 | `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3` | 0.41 | 9.0 |
| S5 | `raw/buscomm-case-3-west-side-united.md` | 0.38 | 6.1 |
| S6 | `raw/marketing-nike-case.md` | 0.37 | 4.8 |

**Gemma's answer** (4.8 s):
> The firm introduced a lower-priced version of its service to accommodate startups, which were
> considered "low type" clients [S1]. This was part of a strategy involving third-degree pricing
> discrimination based on company size and segment [S2]. This allowed the firm to expand its customer
> base and increase revenue by offering a version that startups could afford [S1].

**Citation check:** `answered_with_citations` (S1, S2).

**Assessment: ⚠️ Partial.**
- Retrieval worked, and the main claim is supported by S1: a lower-priced version for "low type"
  clients such as startups.
- The answer does **not name** the service ("strategic introductions") or describe it (the top five
  candidates, limited market mapping), although both are in S1.
- The second sentence merges in S2 (Examples 3, segment-based third-degree pricing). Each citation
  is accurate for its own sentence, but saying the new service was "part of" third-degree
  discrimination is misleading: S1 describes it as versioning, which is second-degree.

Earlier attempts are kept for comparison: E2B with the first rules replied "Insufficient evidence"
([attempt-1](../runs/ask/attempt-1/)); E2B with looser rules answered from the wrong passage
([attempt-3-e2b](../runs/ask/attempt-3-e2b/)). See README §6.

Full run: [`runs/ask/20260922-182147-…`](../runs/ask/20260922-182147-what-cheaper-service-did-my-former-executive-searc.md)

---

## T3: answer connecting two sources

**Question:** What is a sunk cost, and how did I fall into the sunk cost trap at a restaurant?

**Expected sources:** `raw/micro-final-cheat-sheet.md › Costs` (definition) and
`raw/micro-examples-in-the-wild-1.md` (the pizza story).

**Retrieved passages** (both expected sources are in the top 3):

| # | Location | cosine | BM25 |
|---|---|---|---|
| S1 | `raw/micro-examples-in-the-wild-1.md` (analysis paragraph) | 0.56 | 20.1 |
| S2 | `raw/micro-final-cheat-sheet.md › Costs` (first half) | 0.43 | 18.2 |
| S3 | `raw/micro-final-cheat-sheet.md › Costs` (contains "Sunk = cannot be recovered…") | 0.37 | 16.3 |
| S4 | `raw/micro-examples-in-the-wild-1.md` (story paragraph) | 0.37 | 7.6 |
| S5 | `raw/finance-summary.pdf › Lecture 13 (part 2) › p.33` | 0.31 | 10.2 |
| S6 | `raw/marketing-final-cheat-sheet.md › Pricing` | 0.31 | 5.7 |

**Gemma's answer** (7.0 s):
> A sunk cost is a cost that cannot be recovered and is irrelevant for future decisions [S3]. Sunk cost
> mistakes occur when future actions are taken to justify past choices, even though those past costs
> are unchangeable and irrelevant for forward thinking [S1].
>
> In the restaurant example, you had paid for a large pizza, and after eating three slices, you realized
> you were full [S4]. You felt compelled to finish the pizza because you had already paid for it, which
> is an example of falling into the sunk cost trap [S1, S4]. The mistake could have been avoided by
> ordering a smaller pizza or by focusing on future outcomes rather than past costs [S1].

**Citation check:** `answered_with_citations` (S1, S3, S4).

**Assessment: ✅ Pass.** I checked every citation:
- **[S3]** contains *"Sunk = cannot be recovered, irrelevant for decisions"*.
- **[S4]** contains *"After eating three slices (out of eight), I realized I was already full … I
  forced myself to finish the pizza just because I had already paid for it"*.
- **[S1]** contains the "rationalize past choices" and "ordering the small pizza" sentences.

Both sources are used, each for its own claim, and no detail is invented.

Full run: [`runs/ask/20260922-182159-…`](../runs/ask/20260922-182159-what-is-a-sunk-cost-and-how-did-i-fall-into-the-su.md)

---

## T4: unsupported question

**Question:** What WACC did I use in my Kellanova DCF valuation?

**Expected:** no source (the Kellanova model was deliberately not included). The trap is that
`finance-summary.pdf` explains WACC in general.

**Retrieved passages** (all general WACC or valuation material, none about Kellanova):

| # | Location | cosine | BM25 |
|---|---|---|---|
| S1 | `raw/finance-summary.pdf › Lecture 12 › p.30` | 0.39 | 8.6 |
| S2 | `raw/finance-summary.pdf › Lecture 7 › p.10` | 0.35 | 11.8 |
| S3 | `raw/finance-summary.pdf › Lecture 8 › p.13` | 0.35 | 7.7 |
| S4 | `raw/finance-summary.pdf › Lecture 11 › p.26` | 0.32 | 6.8 |
| S5 | `raw/finance-summary.pdf › Lecture 11 › p.26` | 0.29 | 7.2 |
| S6 | `raw/finance-summary.pdf › Lecture 7 › p.10` | 0.27 | 5.2 |

**Gemma's answer** (4.5 s):
> Insufficient evidence: The passages do not contain information about a Kellanova DCF valuation or
> the specific WACC used in it.

**Citation check:** `insufficient_evidence`.

**Assessment: ✅ Pass.** Explicit refusal, and no number was stated despite six WACC-related passages.

Full run: [`runs/ask/20260922-182209-…`](../runs/ask/20260922-182209-what-wacc-did-i-use-in-my-kellanova-dcf-valuation.md)

---

## Mode checks in the same offline recording

| Check | Result |
|---|---|
| Chat: "what can you help me with?" | ✅ Accurate list of capabilities; no notes lookup (*conversational turn*); no citations or refusal |
| Chat: "Draft a short 5-day study plan for my Microeconomics final using my notes." | ✅ Looked up 4 Microeconomics passages (course named) and cited them as [N1]-[N4] |
| Chat: "make that shorter" | ✅ No lookup; shortened the plan from the conversation |
| Chat: "For the record, my Kellanova WACC was 9%." | ⚠️ Correctly said the fact is kept only for this conversation and is not in the wiki, but it also said "I've noted that" and wrongly claimed there is no Finance section (there is one; only Kellanova is missing) |
| Ask, right after: the Kellanova WACC question | ✅ `insufficient_evidence`: the chat claim was not treated as evidence |
| Search: `price discrimination` | ✅ 3 original passages with paths; no generated answer; ran without loading Gemma |

Chat transcript: [`runs/chat/20260922-182255-session.md`](../runs/chat/20260922-182255-session.md) ·
Search output: [`runs/search/20260922-182125-price-discrimination.md`](../runs/search/20260922-182125-price-discrimination.md) ·
Ingest (one source, re-ingested with `--force`): [`runs/ingest/20260922-182123-ingest.md`](../runs/ingest/20260922-182123-ingest.md)
