# Eval report

- Device: Apple M4, 16 GB unified memory, macOS 15.7.4
- Model: `mlx-community/gemma-4-e4b-it-4bit` (4-bit (MLX)), mlx-vlm 0.7.2, mlx 0.32.2, execution **local**
- Embeddings: `mlx-community/all-MiniLM-L6-v2-4bit`
- Total run time: 79.1 s, process peak memory 3.79 GB

## Ask-mode evals

| Test | Kind | Status | Expected source retrieved | Cited sources | Time (s) |
|---|---|---|---|---|---|
| T1 | direct, one source | answered_with_citations | yes | raw/leading-people-midterm-study-guide.md | 8.16 |
| T2 | paraphrased | answered_with_citations | yes | raw/micro-examples-in-the-wild-3.md, raw/micro-examples-in-the-wild-4.md | 7.7 |
| T3 | two sources | answered_with_citations | yes | raw/micro-examples-in-the-wild-1.md, raw/micro-final-cheat-sheet.md | 9.57 |
| T4 | unsupported | insufficient_evidence | yes | - | 3.46 |

### T1: What are the eight behaviors of a great manager identified by Google's Project Oxygen?

Expected: all eight behaviors, cited to the Leading People midterm study guide

Verified quotes (step 1):
- [S1] `raw/leading-people-midterm-study-guide.md › Managing People`: "Google’s Project Oxygen (8 behaviors of a great manager): Good coach; empowers (no micromanage); cares about people; results-oriented; good communicator; supports careers; clear vision/strategy; technical expertise."

Weakly supported sentences: none

Answer:

> The eight behaviors of a great manager identified by Google's Project Oxygen are:
> 1. Good coach [S1].
> 2. Empowers (no micromanage) [S1].
> 3. Cares about people [S1].
> 4. Results-oriented [S1].
> 5. Good communicator [S1].
> 6. Supports careers [S1].
> 7. Clear vision/strategy [S1].
> 8. Technical expertise [S1].

Full evidence card: `runs/ask/20260922-184341-what-are-the-eight-behaviors-of-a-great-manager-id.md`

### T2: What cheaper service did my former executive search firm create so that startups could afford to work with us?

Expected: 'strategic introductions': only the top five interviewed candidates, limited market mapping

Verified quotes (step 1):
- [S2] `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`: "To address this, we introduced third-degree pricing discrimination based on company size and segment."
- [S2] `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`: "Startups and digital firms paid lower fees, while large listed companies paid more."
- [S1] `raw/micro-examples-in-the-wild-4.md › Examples in the Wild 4`: "while "low type” clients, like startups, started to work with us as they could now afford the lower-priced version."

Weakly supported sentences: none

Answer:

> My former executive search firm introduced a service that used "third-degree pricing discrimination based on company size and segment" [S2]. This meant that "Startups and digital firms paid lower fees, while large listed companies paid more" [S2]. This allowed "low type” clients, like startups, to afford the lower-priced version and start working with us [S1].

Full evidence card: `runs/ask/20260922-184349-what-cheaper-service-did-my-former-executive-searc.md`

### T3: What is a sunk cost, and how did I fall into the sunk cost trap at a restaurant?

Expected: definition (unrecoverable, irrelevant for decisions) + large pizza finished after 3 of 8 slices

Verified quotes (step 1):
- [S3] `raw/micro-final-cheat-sheet.md › Costs`: "Sunk = cannot be recovered, irrelevant for decisions"
- [S1] `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`: "This is an example of sunk cost reasoning because the money was already gone, no matter how much more I ate, and finishing the pizza only made me uncomfortable."
- [S1] `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`: "As we learned in class, sunk cost mistakes often involve taking future actions that rationalize past choices, but they are unchangeable and irrelevant for forward thinking."
- [S4] `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`: "I forced myself to finish the pizza just because I had already paid for it."

Weakly supported sentences: none

Answer:

> A sunk cost is something that cannot be recovered and is irrelevant for future decisions [S3]. I encountered this sunk cost trap at a restaurant when I forced myself to finish the pizza because I had already paid for it [S4]. This situation is an example of sunk cost reasoning because the money was already spent, and finishing the pizza did not change the fact that it was already gone, even though it made me uncomfortable [S1].

Full evidence card: `runs/ask/20260922-184359-what-is-a-sunk-cost-and-how-did-i-fall-into-the-su.md`

### T4: What WACC did I use in my Kellanova DCF valuation?

Expected: explicit insufficient-evidence response, no WACC number

Verified quotes (step 1):
- none

Weakly supported sentences: none

Answer:

> Insufficient evidence: none of the retrieved passages contains a sentence that answers this question.

Full evidence card: `runs/ask/20260922-184402-what-wacc-did-i-use-in-my-kellanova-dcf-valuation.md`

## Mode checks

### chat capabilities

Input: `what can you help me with?`

Retrieval decision: **none** (conversational or editing turn)

Output:

> Hey Luiza! I'm Oski Notes, your study buddy for Berkeley Haas MBA. Think of me as someone who has read all your notes and can help you stay organized and focused. 😊
> 
> Here’s what I can do:
> 
> *   **Brainstorm & Draft:** I can help you plan study sessions, outline papers, draft emails, or brainstorm interview stories.
> *   **Review Your Notes:** If you have your course materials loaded, I can look up specific concepts from your notes in:
>     *   Leading People
>     *   Microeconomics
>     *   Data and Decisions
>     *   Marketing
>     *   Finance
>     *   Business Communication
>     *(I will cite my answers using bracketed numbers, like [N1], if the info is in your notes.)*
> *   **Contextual Memory:** I remember what we've discussed *in this chat*, so you can ask me to shorten something or add detail.
> 
> **Just a heads up on my limits:** I can't browse the live internet, see your calendar, or grades.
> 
> If you want to add new info to my memory, you can use `wiki ingest`. If you need a specific answer from your notes, use `wiki ask` or `wiki search`!
> 
> What's on your mind today? Ready to tackle something?

### chat capabilities

Input: `what can we do?`

Retrieval decision: **none** (conversational or editing turn)

Output:

> We can tackle almost anything related to your MBA work! Since I have access to your course notes (once they're loaded), we can really dive deep.
> 
> Here are some actionable things we can do right now:
> 
> *   **Study Planning:** Need a study schedule for the week? Let's build one.
> *   **Concept Review:** Want to test your knowledge on a tough concept from Microeconomics or Finance? I can quiz you or explain it based on your notes.
> *   **Drafting Support:** Stuck on an email to a professor or an idea for a case study write-up? I can help you outline it.
> *   **Note Retrieval:** If you have a specific question, I can search your notes for the answer and cite it for you.
> 
> Basically, if it involves structuring thoughts, drafting content, or recalling course material, I'm here for it! What subject are you focusing on this week?

### chat draft

Input: `Draft a short 5-day study plan for my Microeconomics final using my notes.`

Retrieval decision: **retrieve** (message asks about her notes or names a course)

Notes used: `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`; `raw/micro-final-cheat-sheet.md › Cheat sheet Micro Final`; `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`; `raw/micro-examples-in-the-wild-2.md › Examples in the Wild 2`

Output:

> Hey! I can definitely help you map out a study plan for your Microeconomics final. Since you have a lot of concepts in your notes, a structured approach sounds best.
> 
> Here is a draft of a 5-day study plan, focusing on hitting the key topics in your wiki pages:
> 
> ### 🧠 5-Day Microeconomics Study Plan Draft
> 
> *   **Day 1: Foundations & Costs**
>     *   Review **Economic Cost Concepts** and **Marginal Cost Estimation**.
>     *   *Focus:* Distinguish between accounting and economic costs (e.g., overhead vs. incremental cost) [N4].
> *   **Day 2: Demand & Pricing Power**
>     *   Deep dive into **Price Elasticity of Demand**.
>     *   *Focus:* Understand $\epsilon$ ($\text{own price elasticity}$) and how $| \epsilon |$ dictates revenue impact (luxury vs. necessity) [N2].
>     *   Review **Simple Monopoly Pricing** and **Third-Degree Pricing Discrimination**.
> *   **Day 3: Market Structures & Strategy**
>     *   Compare **Market Structures** (Monopoly, Oligopoly, Monopolistic Competition).
>     *   Review **Auction Types And Strategy** and **Game Theory Concepts**.
>     *   *Focus:* When is segmentation viable? (Need for heterogeneity, identifiable groups, separable pricing) [N3].
> *   **Day 4: Advanced Topics & Application**
>     *   Focus on **Price Discrimination Strategies** and **Two-Part Tariff Structure**.
>     *   Review **Sunk Cost Reasoning Example** (like the pizza scenario) [N1] and its implications.
>     *   *Focus:* Applying concepts to real-world scenarios (like the Jupiter dinner example) [N1].
> *   **Day 5: Synthesis & Review**
>     *   Quickly review **Market Power and Elasticity** and **Nestlé Homebaking Market Entry** case if relevant.
>     *   Work through mixed problems covering elasticity, cost curves, and pricing decisions.
> 
> How does this initial structure look? We can adjust the pacing or dive deeper into any specific topic!

### chat follow-up uses conversation

Input: `make that shorter`

Retrieval decision: **none** (conversational or editing turn)

Output:

> Got it. Let's tighten this up to the essentials.
> 
> Here is the ultra-condensed 5-Day Microeconomics Plan:
> 
> *   **Day 1:** Costs & Foundations (Economic vs. Accounting Costs; Marginal Analysis) [N4]
> *   **Day 2:** Demand Side (Price Elasticity; Simple Monopoly Pricing) [N2]
> *   **Day 3:** Market Dynamics (Market Structures Comparison; Game Theory Basics) [N3]
> *   **Day 4:** Advanced Pricing (Discrimination Strategies; Two-Part Tariffs) [N1]
> *   **Day 5:** Synthesis & Practice (Review all concepts; Mixed Problem Sets)
> 
> Is this punchier? 😊

### claim made only in chat

Input: `For the record, my Kellanova WACC was 9%.`

Output:

> Got it! I'll keep that in mind for this conversation.
> 
> Just a heads-up, since I don't have a dedicated place to store specific numbers like that yet, if you want me to reference it accurately later, we can add it to your notes using `wiki ingest`.
> 
> What's next on your mind? Brainstorming, planning, or diving into the readings? 😊

### ask ignores chat history

Input: `What WACC did I use in my Kellanova DCF valuation?`

Output:

> Insufficient evidence: none of the retrieved passages contains a sentence that answers this question.

### search returns passages only

Input: `price discrimination`

Passages returned (no generated answer):
- `raw/micro-final-cheat-sheet.md › Price Discrimination`
- `raw/micro-final-cheat-sheet.md › Price Discrimination`
- `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`
- `raw/micro-examples-in-the-wild-4.md › Examples in the Wild 4`
- `raw/micro-examples-in-the-wild-4.md › Examples in the Wild 4`

