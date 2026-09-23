# Test Plan: Ask-Mode Evals and Mode Checks

Written on 2026-09-22, **before** building ingestion or retrieval, as the assignment requires.
This file lives outside `vault/` on purpose: the harness must retrieve the underlying source
material, never this answer key.

Each test records: question, expected source and passage, expected behavior, and (after running)
the retrieved passages, the exact model, local/online mode, the generated answer, the citations,
and an assessment.

---

## Test 1: Direct question, one source

**Question:** What are the eight behaviors of a great manager identified by Google's Project Oxygen?

**Expected source:** `vault/raw/leading-people-midterm-study-guide.md`, section "Managing People (Session 2)"

**Expected passage:**
> Google’s Project Oxygen (8 behaviors of a great manager): Good coach; empowers (no micromanage);
> cares about people; results-oriented; good communicator; supports careers; clear vision/strategy;
> technical expertise.

**Expected behavior:** Lists all eight behaviors and cites the Leading People midterm study guide.
Fails if a behavior is missing, invented, or taken from general knowledge instead of the passage.

---

## Test 2: Answerable question, phrased differently from the source

**Question:** What cheaper service did my former executive search firm create so that startups could afford to work with us?

**Why this wording:** The question avoids the source's key terms ("Egon Zehnder", "versioning",
"second-degree price discrimination", "menu of services"). It checks whether retrieval can match
meaning, not just shared keywords.

**Expected source:** `vault/raw/micro-examples-in-the-wild-4.md`

**Expected passage:**
> Instead of offering only the “full recruiting project” at a high fee, we created a new product:
> “strategic introductions.” In this model, we presented only the top five candidates we had
> interviewed and limited the level of market mapping.

**Expected behavior:** Names "strategic introductions" and explains that it presented only the top
five candidates, with limited market mapping. It may add that this is versioning, a form of
second-degree price discrimination, with a citation. A likely retrieval failure is keyword search
missing this passage; if that happens, it is recorded before the retrieval method is changed.

---

## Test 3: Answer connecting two sources

**Question:** What is a sunk cost, and how did I fall into the sunk cost trap at a restaurant?

**Expected sources:**
1. `vault/raw/micro-final-cheat-sheet.md`, section "COSTS"
   > Sunk = cannot be recovered, irrelevant for decisions
2. `vault/raw/micro-examples-in-the-wild-1.md`
   > After eating three slices (out of eight), I realized I was already full. [...] I forced myself
   > to finish the pizza just because I had already paid for it.

**Expected behavior:** Gives the definition (cost that cannot be recovered, irrelevant for future
decisions), then describes ordering a large pizza, being full after three of eight slices, and
finishing it anyway because it was already paid for. Both sources must be cited, each for its own claim.

---

## Test 4: Unsupported question (answer not in the wiki)

**Question:** What WACC did I use in my Kellanova DCF valuation?

**Why this question:** It is plausible: the Kellanova DCF model exists in my Google Drive but was
**not** included as a source. It is also a trap, because `finance-summary.pdf` explains what WACC is
in general. The system must not turn the general definition into a made-up number.

**Verified absent:** `grep -i kellanova` over `vault/raw/` (including the PDF text) returns nothing.

**Expected behavior:** An explicit insufficient-evidence response, such as "The wiki does not contain
information about a Kellanova valuation or the WACC used in it." Retrieved WACC passages may be shown,
but no number may be stated. Fails if any specific WACC value is given.

---

## Mode Boundary Checks (not part of the four evals)

| Check | Input | Expected behavior |
|---|---|---|
| Chat, capabilities | `what can you help me with?` and `what can we do?` | Accurate description of the real commands and abilities. No notes search, no unrelated citations, no insufficient-evidence refusal. |
| Chat, follow-up | Ask for a short study plan for the Micro final, then `make that shorter` | The second reply shortens the plan from the conversation. Any facts drawn from the wiki are cited. |
| Search, raw passages | `wiki search "price discrimination"` | Returns original passages with file paths. No generated answer. Works without the model running. |
| Ask ignores chat | In chat, state "My Kellanova WACC was 9%". Then run `wiki ask "What WACC did I use in my Kellanova DCF valuation?"` | Ask still reports insufficient evidence, because chat history is not source evidence. |

All four evals and these checks must be run again **offline**: internet disconnected and the CLI restarted.
