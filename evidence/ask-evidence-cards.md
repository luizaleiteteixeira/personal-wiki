# Ask-mode evidence cards (offline run, two-step ask)

**Run:** 2026-09-22, 18:41-18:43 PDT, recorded in [`offline-demo.cast`](offline-demo.cast) /
[`offline-demo.gif`](offline-demo.gif). The recording starts by showing `Wi-Fi Power (en0): Off` and
`curl: (6) Could not resolve host: huggingface.co`. Every command is a new CLI process.

**Model:** `mlx-community/gemma-4-e4b-it-4bit` (Gemma 4 E4B, instruction-tuned, 4-bit MLX), runtime
mlx-vlm 0.7.2 / mlx 0.32.2, execution **local**, temperature 0.
**Retrieval:** hybrid BM25 + `mlx-community/all-MiniLM-L6-v2-4bit` embeddings (RRF), top 6 passages.
**Device:** Apple M4, 16 GB unified memory, macOS 15.7.4.

**How ask works in this run** (changed after the first evaluation, see README §6):
1. **Extract:** Gemma copies, word for word, the sentences that answer the question
   (`prompts/extract-instructions.md`).
2. **Verify:** the harness keeps a quote only if it really occurs in the passage it claims. If no quote
   survives, the harness answers "insufficient evidence" itself.
3. **Answer:** Gemma answers from the verified quotes only (`prompts/wiki-instructions.md`).
4. **Check:** each cited sentence is compared with its passage, and low word overlap is flagged.

Expectations were written before building, in [`../tests/test-plan.md`](../tests/test-plan.md).
The assessments are mine, made by opening each cited passage. The first, single-step version of these
cards is in [`previous/`](previous/ask-evidence-cards-v1-single-step.md).

---

## T1: direct question, one source

**Question:** What are the eight behaviors of a great manager identified by Google's Project Oxygen?

**Expected source:** `raw/leading-people-midterm-study-guide.md › Managing People`

**Retrieved passages** (the expected one is ranked first):

| # | Location | cosine | BM25 |
|---|---|---|---|
| S1 | `raw/leading-people-midterm-study-guide.md › Managing People` | 0.67 | 21.2 |
| S2 | `raw/leading-people-midterm-study-guide.md › Introduction: Leadership vs. Management` | 0.43 | 8.8 |
| S3 | `raw/micro-examples-in-the-wild-2.md` | 0.40 | 4.1 |
| S4 | `raw/leading-people-final-study-guide.md › Macro Interactions — Change` | 0.39 | 3.7 |
| S5 | `raw/marketing-final-cheat-sheet.md › Module 2: Market Research & Consumer Insights` | 0.38 | 3.7 |
| S6 | `raw/leading-people-final-study-guide.md › Complex Interactions — Persuasion` | 0.32 | 5.5 |

**Verified quote (step 1):**
- [S1] "Google’s Project Oxygen (8 behaviors of a great manager): Good coach; empowers (no micromanage); cares about people; results-oriented; good communicator; supports careers; clear vision/strategy; technical expertise."

**Gemma's answer** (8.3 s = 4.8 s extract + 3.5 s answer, MLX peak 5.87 GB):
> The eight behaviors of a great manager identified by Google's Project Oxygen are: 1. Good coach [S1].
> 2. Empowers (no micromanage) [S1]. 3. Cares about people [S1]. 4. Results-oriented [S1].
> 5. Good communicator [S1]. 6. Supports careers [S1]. 7. Clear vision/strategy [S1]. 8. Technical expertise [S1].

**Checks:** `answered_with_citations`; support check flagged 0 sentences.

**Assessment: ✅ Pass.** The answer reproduces the verified quote exactly, in the same order, with nothing added.

Full run: [`runs/ask/20260922-184148-…`](../runs/ask/20260922-184148-what-are-the-eight-behaviors-of-a-great-manager-id.md)

---

## T2: answerable question, phrased differently from the source

**Question:** What cheaper service did my former executive search firm create so that startups could afford to work with us?

**Expected source:** `raw/micro-examples-in-the-wild-4.md`: *"we created a new product: 'strategic
introductions.' In this model, we presented only the top five candidates we had interviewed and
limited the level of market mapping."*

**Retrieved passages:** the expected passage is ranked first (S1), even though the question shares none of its key terms.

| # | Location | cosine | BM25 |
|---|---|---|---|
| S1 | `raw/micro-examples-in-the-wild-4.md` | 0.50 | 27.5 |
| S2 | `raw/micro-examples-in-the-wild-3.md` | 0.52 | 14.6 |
| S3 | `raw/micro-examples-in-the-wild-2.md` | 0.46 | 22.0 |
| S4 | `raw/micro-examples-in-the-wild-3.md` | 0.41 | 9.0 |
| S5 | `raw/buscomm-case-3-west-side-united.md` | 0.38 | 6.1 |
| S6 | `raw/marketing-nike-case.md` | 0.37 | 4.8 |

**Verified quotes (step 1):**
- [S2] "To address this, we introduced third-degree pricing discrimination based on company size and segment."
- [S2] "Startups and digital firms paid lower fees, while large listed companies paid more."
- [S1] "while 'low type' clients, like startups, started to work with us as they could now afford the lower-priced version."

**Gemma's answer** (8.2 s):
> My former executive search firm introduced a service that used "third-degree pricing discrimination
> based on company size and segment" [S2]. This meant that "Startups and digital firms paid lower fees,
> while large listed companies paid more" [S2]. This allowed "low type” clients, like startups, to
> afford the lower-priced version and start working with us [S1].

**Checks:** `answered_with_citations`; support check flagged 0 sentences.

**Assessment: ⚠️ Partial, not improved.**
- All three quotes are real and each is cited to the right passage.
- Step 1 still did not select the sentence that names the service ("strategic introductions") or
  describes it (the top five candidates, limited market mapping).
- The first sentence is misleading. It presents segment pricing from Examples 3 as "a service", then
  links it to the lower-priced version from Examples 4. The notes describe these as two different
  moves: third-degree pricing first, and then versioning (second-degree) to fix its problems.
- The support check did not catch this blend, because every word in the sentence appears in the
  cited passages. Word overlap cannot detect a wrong connection between true facts.

Full run: [`runs/ask/20260922-184201-…`](../runs/ask/20260922-184201-what-cheaper-service-did-my-former-executive-searc.md)

---

## T3: answer connecting two sources

**Question:** What is a sunk cost, and how did I fall into the sunk cost trap at a restaurant?

**Expected sources:** `raw/micro-final-cheat-sheet.md › Costs` (definition) and
`raw/micro-examples-in-the-wild-1.md` (the pizza story). Both are in the top 3 (S1, S2/S3, plus S4).

**Verified quotes (step 1):**
- [S3] "Sunk = cannot be recovered, irrelevant for decisions" (`micro-final-cheat-sheet.md › Costs`)
- [S1] "This is an example of sunk cost reasoning because the money was already gone, no matter how much more I ate, and finishing the pizza only made me uncomfortable."
- [S1] "As we learned in class, sunk cost mistakes often involve taking future actions that rationalize past choices, but they are unchangeable and irrelevant for forward thinking."
- [S4] "I forced myself to finish the pizza just because I had already paid for it."

**Gemma's answer** (10.0 s):
> A sunk cost is something that cannot be recovered and is irrelevant for future decisions [S3]. I
> encountered this sunk cost trap at a restaurant when I forced myself to finish the pizza because I had
> already paid for it [S4]. This situation is an example of sunk cost reasoning because the money was
> already spent, and finishing the pizza did not change the fact that it was already gone, even though
> it made me uncomfortable [S1].

**Checks:** `answered_with_citations` (S1, S3, S4); support check flagged 0 sentences.

**Assessment: ✅ Pass, and better grounded than the first version.** Each sentence restates exactly one
verified quote, and both sources are used. Compared with the first version, it no longer adds
unquoted details (three slices, the smaller pizza). Those details are true, but they could not be
verified sentence by sentence.

Full run: [`runs/ask/20260922-184216-…`](../runs/ask/20260922-184216-what-is-a-sunk-cost-and-how-did-i-fall-into-the-su.md)

---

## T4: unsupported question

**Question:** What WACC did I use in my Kellanova DCF valuation?

**Expected:** no source. The trap is that six general WACC and valuation passages from
`finance-summary.pdf` are retrieved (Lectures 7, 8, 11 and 12).

**Verified quotes (step 1):** none. Gemma output `NONE`.

**Answer** (3.9 s, one model call; the harness answered without step 2):
> Insufficient evidence: none of the retrieved passages contains a sentence that answers this question.

**Checks:** `insufficient_evidence`.

**Assessment: ✅ Pass.** The refusal is now enforced by the harness: with no verifiable quote, Gemma is
never asked to write an answer, so it cannot produce a number.

Full run: [`runs/ask/20260922-184225-…`](../runs/ask/20260922-184225-what-wacc-did-i-use-in-my-kellanova-dcf-valuation.md)

---

## Mode checks in the same offline recording

| Check | Result |
|---|---|
| Chat: "what can you help me with?" | ✅ Accurate list of capabilities; no notes lookup (*conversational turn*) |
| Chat: "Draft a short 5-day study plan for my Microeconomics final using my notes." | ✅ Looked up Microeconomics passages only (course named) and used the course's wiki page titles as a topic map |
| Chat: "make that shorter" | ✅ No lookup; shortened the plan from the conversation |
| Chat: "For the record, my Kellanova WACC was 9%." | ✅ The harness guardrail caught a first draft that claimed to have saved the fact and regenerated it. Final reply: *"that information is noted here for this conversation, but it is **not** in your current study notes or wiki"*, suggesting `wiki ingest` (visible in the recording as `(guardrail: rewrote a reply…)`) |
| Ask, right after: the Kellanova WACC question | ✅ `insufficient_evidence`: the chat claim was not treated as evidence |
| Search: `price discrimination` | ✅ 3 original passages with paths; no generated answer; ran without loading Gemma |

Chat transcript: [`runs/chat/20260922-184317-session.md`](../runs/chat/20260922-184317-session.md) ·
Search output: [`runs/search/20260922-184134-price-discrimination.md`](../runs/search/20260922-184134-price-discrimination.md) ·
Ingest (one source, re-ingested with `--force`): [`runs/ingest/20260922-184132-ingest.md`](../runs/ingest/20260922-184132-ingest.md) ·
Full eval report (run right after the demo): [`eval-report.md`](eval-report.md)
