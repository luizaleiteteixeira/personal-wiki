# Eval report

- Device: Apple M4, 16 GB unified memory, macOS 15.7.4
- Model: `mlx-community/gemma-4-e4b-it-4bit` (4-bit (MLX)), mlx-vlm 0.7.2, mlx 0.32.2, execution **local**
- Embeddings: `mlx-community/all-MiniLM-L6-v2-4bit`
- Total run time: 69.6 s, process peak memory 3.13 GB

## Ask-mode evals

| Test | Kind | Status | Expected source retrieved | Cited sources | Time (s) |
|---|---|---|---|---|---|
| T1 | direct, one source | answered_with_citations | yes | raw/leading-people-midterm-study-guide.md | 6.87 |
| T2 | paraphrased | answered_with_citations | yes | raw/micro-examples-in-the-wild-3.md, raw/micro-examples-in-the-wild-4.md | 5.05 |
| T3 | two sources | answered_with_citations | yes | raw/micro-examples-in-the-wild-1.md, raw/micro-final-cheat-sheet.md | 7.17 |
| T4 | unsupported | insufficient_evidence | yes | - | 4.92 |

### T1: What are the eight behaviors of a great manager identified by Google's Project Oxygen?

Expected: all eight behaviors, cited to the Leading People midterm study guide

Answer:

> The eight behaviors of a great manager, according to Google’s Project Oxygen, are:
> 1. Good coach [S1].
> 2. Empowers (does not micromanage) [S1].
> 3. Cares about people [S1].
> 4. Is results-oriented [S1].
> 5. Is a good communicator [S1].
> 6. Supports careers [S1].
> 7. Has a clear vision/strategy [S1].
> 8. Possesses technical expertise [S1].

Full evidence card: `runs/ask/20260922-175859-what-are-the-eight-behaviors-of-a-great-manager-id.md`

### T2: What cheaper service did my former executive search firm create so that startups could afford to work with us?

Expected: 'strategic introductions': only the top five interviewed candidates, limited market mapping

Answer:

> The firm introduced a lower-priced version of its service to accommodate startups, which were considered "low type" clients [S1]. This was part of a strategy involving third-degree pricing discrimination based on company size and segment [S2]. This allowed the firm to expand its customer base and increase revenue by offering a version that startups could afford [S1].

Full evidence card: `runs/ask/20260922-175904-what-cheaper-service-did-my-former-executive-searc.md`

### T3: What is a sunk cost, and how did I fall into the sunk cost trap at a restaurant?

Expected: definition (unrecoverable, irrelevant for decisions) + large pizza finished after 3 of 8 slices

Answer:

> A sunk cost is a cost that cannot be recovered and is irrelevant for future decisions [S3]. Sunk cost mistakes occur when future actions are taken to justify past choices, even though those past costs are unchangeable and irrelevant for forward thinking [S1].
> 
> In the restaurant example, you had paid for a large pizza, and after eating three slices, you realized you were full [S4]. You felt compelled to finish the pizza because you had already paid for it, which is an example of falling into the sunk cost trap [S1, S4]. The mistake could have been avoided by ordering a smaller pizza or by focusing on future outcomes rather than past costs [S1].

Full evidence card: `runs/ask/20260922-175911-what-is-a-sunk-cost-and-how-did-i-fall-into-the-su.md`

### T4: What WACC did I use in my Kellanova DCF valuation?

Expected: explicit insufficient-evidence response, no WACC number

Answer:

> Insufficient evidence: The passages do not contain information about a Kellanova DCF valuation or the specific WACC used in it.

Full evidence card: `runs/ask/20260922-175916-what-wacc-did-i-use-in-my-kellanova-dcf-valuation.md`

## Mode checks

### chat capabilities

Input: `what can you help me with?`

Retrieval decision: **none** (conversational or editing turn)

Output:

> Hey Luiza! Think of me as your dedicated study buddy for Haas. I'm here to help you crush this MBA stuff! 🚀
> 
> Here’s what I can do:
> 
> *   **Brainstorm & Draft:** Need to outline a presentation, draft an email, or map out an interview story? I can help with that.
> *   **Study Support (Using Your Notes):** I can pull up passages from your personal wiki across all your courses (Leading People, Microeconomics, Data & Decisions, Marketing, Finance, Business Comm) if you use the `wiki ask` command.
> *   **Contextual Memory:** I remember what we've discussed *in this chat*, so you can always say "make that shorter" or "add an example."
> 
> **Just remember:** I can't browse the live internet, see your grades, or access your calendar.
> 
> If you want me to look up something specific from your notes, you'll need to use `wiki ask` or `wiki search`! What's on your mind today? 😊

### chat capabilities

Input: `what can we do?`

Retrieval decision: **none** (conversational or editing turn)

Output:

> We can tackle almost anything related to your Haas MBA work! Since I'm here to support your studies, here are some specific things we can jump on right now:
> 
> *   **Planning:** Developing study schedules, structuring outlines for projects, or planning approaches for tough concepts.
> *   **Writing Support:** Drafting emails, refining case study takeaways, or brainstorming narratives for career stories.
> *   **Note Review:** If you paste in a Topic Map, we can use those page titles to structure a recap or a study plan.
> *   **Deep Dive (with your notes):** If you use `wiki ask`, I can answer questions based *only* on the material you've loaded into your personal wiki for courses like Finance or Marketing.
> 
> Basically, if it involves organizing thoughts or structuring information for your MBA, I'm ready! What's the next task?

### chat draft

Input: `Draft a short 5-day study plan for my Microeconomics final using my notes.`

Retrieval decision: **retrieve** (message asks about her notes or names a course)

Notes used: `raw/marketing-final-cheat-sheet.md › MBA 206: Marketing Study Guide — Key Frameworks Summary`; `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`; `raw/leading-people-final-study-guide.md › Complex Interactions — Negotiations`; `raw/marketing-final-cheat-sheet.md › MBA 206: Marketing Study Guide — Module 4: Special Topics`

Output:

> Hey! I can definitely help you map out a study plan. Since you're focusing on Microeconomics, I'll structure this around the topics in your wiki pages and keep it high-level.
> 
> Here is a suggested 5-day plan to cover the material:
> 
> *   **Day 1: Foundations**
>     *   Review: Economic Cost Concepts & Sunk Cost Reasoning Example.
>     *   Focus: Understanding the difference between various costs.
> *   **Day 2: Market Structures**
>     *   Review: Simple Monopoly Pricing, Oligopoly Market Structure, Monopolistic Competition Market Structure.
>     *   Focus: How different market conditions affect pricing and behavior.
> *   **Day 3: Pricing & Demand**
>     *   Review: Price Elasticity of Demand, Third-Degree Pricing Discrimination, Two-Part Tariff Structure.
>     *   Focus: Applying pricing strategies based on market conditions.
> *   **Day 4: Advanced Topics**
>     *   Review: Auction Types And Strategy, Game Theory Concepts, Market Power and Elasticity.
>     *   Focus: Strategic decision-making in markets.
> *   **Day 5: Synthesis & Practice**
>     *   Review: Marginal Cost Estimation, Nestlé Homebaking Market Entry.
>     *   Focus: Putting concepts together; work through practice problems.
> 
> How does that look? We can adjust the pacing or dive into specific topics if you want to start drafting flashcards or practice questions for any of those pages! 😊

### chat follow-up uses conversation

Input: `make that shorter`

Retrieval decision: **none** (conversational or editing turn)

Output:

> Sure, here is the ultra-concise version:
> 
> *   **Day 1:** Costs & Foundations
> *   **Day 2:** Market Structures (Monopoly/Oligopoly)
> *   **Day 3:** Pricing & Demand Elasticity
> *   **Day 4:** Advanced Topics (Auctions/Game Theory)
> *   **Day 5:** Synthesis & Practice Problems
> 
> Ready to tackle any of those days? 💪

### claim made only in chat

Input: `For the record, my Kellanova WACC was 9%.`

Output:

> Got it! I'll keep that in mind for our current conversation. Just a heads-up, since I don't have a dedicated "vault" or memory outside of this chat session, if you want me to officially add that to your notes for future reference, you'll need to use the `wiki ingest` command. 😊

### ask ignores chat history

Input: `What WACC did I use in my Kellanova DCF valuation?`

Output:

> Insufficient evidence: The passages do not contain information about a Kellanova DCF valuation or the specific WACC used in it.

### search returns passages only

Input: `price discrimination`

Passages returned (no generated answer):
- `raw/micro-final-cheat-sheet.md › Price Discrimination`
- `raw/micro-final-cheat-sheet.md › Price Discrimination`
- `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`
- `raw/micro-examples-in-the-wild-4.md › Examples in the Wild 4`
- `raw/micro-examples-in-the-wild-4.md › Examples in the Wild 4`

