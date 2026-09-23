# Ask: What is a sunk cost, and how did I fall into the sunk cost trap at a restaurant?

- Model: `mlx-community/gemma-4-e4b-it-4bit` (4-bit (MLX)), runtime mlx-vlm 0.7.2, mlx 0.32.2, execution: **local**
- Embeddings: `mlx-community/all-MiniLM-L6-v2-4bit`
- Citation check: **answered_with_citations**, weakly supported sentences: 0
- Generation: 10.03 s (steps [6.6, 3.43]), 1811 prompt tokens, 203 output tokens, MLX peak memory 5.9 GB

## Answer

A sunk cost is something that cannot be recovered and is irrelevant for future decisions [S3]. I encountered this sunk cost trap at a restaurant when I forced myself to finish the pizza because I had already paid for it [S4]. This situation is an example of sunk cost reasoning because the money was already spent, and finishing the pizza did not change the fact that it was already gone, even though it made me uncomfortable [S1].

## Citations

- [S1] `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`
- [S3] `raw/micro-final-cheat-sheet.md › Costs`
- [S4] `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`

## Step 1: verified quotes

- [S3] `raw/micro-final-cheat-sheet.md › Costs`: "Sunk = cannot be recovered, irrelevant for decisions"
- [S1] `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`: "This is an example of sunk cost reasoning because the money was already gone, no matter how much more I ate, and finishing the pizza only made me uncomfortable."
- [S1] `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`: "As we learned in class, sunk cost mistakes often involve taking future actions that rationalize past choices, but they are unchangeable and irrelevant for forward thinking."
- [S4] `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`: "I forced myself to finish the pizza just because I had already paid for it."

Rejected quotes:
- none

## Support check

- none

## Retrieved passages

**[S1]** `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`  (fused score 0.0333, cosine 0.560, bm25 20.14)

> This is an example of sunk cost reasoning because the money was already gone, no matter how much more I ate, and finishing the pizza only made me uncomfortable. As we learned in class, sunk cost mistakes often involve taking future actions that rationalize past choices, but they are unchangeable and irrelevant for forward thinking. So, the mistake could have been avoided by ordering the small pizza, or by focusing on future outcomes instead of past costs - accepting the sunk cost and not eating the whole thing once full.
> 
>   
> 
> **Word count: 198**

**[S2]** `raw/micro-final-cheat-sheet.md › Costs`  (fused score 0.0328, cosine 0.430, bm25 18.23)

> DECISION TREE
> EV for each option. If don't know probabilities, calculate the break even point (Ev1 = Ev2)
> Information  pivotal if it changes behavior - if not = no value
> Value of Information: Difference in Expected Payoffs
> COSTS
> ECONOMICAL COST = EXPENDITURES - SUNK COST + OPP.
> Only allocate costs that will change if you make that decision (incremental). Overhead costs are treated as sunk (matter for overall profit, but not for decisions) if it will change - shared overhead fallacy
> TYPES:
> Average = total cost / Q (review profitability)
> Minimal AC: when AC = MC → minimum price to profit
> You only produce when P > AC
> Firm profits when P = AC
> P > AC - positive profit
> If the best (P=MC) has neg. profits, the firm should not produce. P < AC - negative profit (chose q=0 if can avoid fixed cost). If fixed are sunk, chose q=0 when P < MC.
> Going down - economy of scale. Up - diseconomy of scale

**[S3]** `raw/micro-final-cheat-sheet.md › Costs`  (fused score 0.0320, cosine 0.367, bm25 16.26)

> Marginal = cost to produce one more unit. Derivative of TC
> Maximizing profit → P = MC (Profit = P x Q – Costs → 0)
> Quantity when MC<P - can produce more to have more profit; if MC>P - have to produce less
> Sunk = cannot be recovered, irrelevant for decisions
> Opportunity = value of the most highly valued alternative foregone
> Total cost = AC x Q

**[S4]** `raw/micro-examples-in-the-wild-1.md › Examples in the Wild 1`  (fused score 0.0315, cosine 0.371, bm25 7.58)

> This weekend I went to dinner at Jupiter with two second-years I met that day. I had been to the restaurant before and ordered one small pizza. However, since I had skipped lunch and the two second-years ordered large pizzas, I thought: “I’m hungry, the large is not much more expensive - why not?”. 
> 
> After eating three slices (out of eight), I realized I was already full. The restaurant didn't have take-out boxes, so I couldn’t save the rest for later. That was the moment I realized I had spent more money than I needed. I forced myself to finish the pizza just because I had already paid for it.

**[S5]** `raw/finance-summary.pdf › Lecture 13 (part 2) › p.33`  (fused score 0.0304, cosine 0.311, bm25 10.20)

> Think incrementally: compare the world if you take the project against the world if you don’t
> Count only cash flows that are caused by the project you are evaluating, but count all of them
> Always ask: would a cash flow still occur even without the project? If yes, it is not incremental to your
> decision, and you should ignore it
> • Ignore sunk costs
> • Ignore any other cash flows that your decision does not affect
> • Account for cash flow effects of your project elsewhere in the firm
> • Account for changes in the timing of cash flows
> • Pay special attention to the cash flows at the end of your project
> • Abandonment costs, liquidation proceeds, etc.
> 
> Valuation
> To value a firm or project
> • Determine its FCF
> • Make the FCF comparable by calculating their present values
> • Compute the present values using your opportunity cost of capital
> 
> The two main drivers of firm (project) values are:

**[S6]** `raw/marketing-final-cheat-sheet.md › Pricing`  (fused score 0.0294, cosine 0.315, bm25 5.66)

> ## **5.4 Pricing Models**
> 
> * Subscription (Nike Adventure Club, streaming)  
> * Freemium (Dropbox, LinkedIn)  
>   * CAC \= cost of maintaining free users. Contribution per user needs to be higher  
> * Bundling  
> * Captive products  
> * Surge pricing (lower price at peak hours to attract new customers / higher price in peak hours)
> 
>   HOW TO PRICE?  
> * Strategy (communication to consumers)  
> * Cost plus (cost \+ desired margin)  
>   * Real state: house is price \+ restoration  
> * Consumer perception and WTP (Market driven) \- what do they value and want?  
>   * Luxury companies (perceived)  
> * Breakeven (no profit)
> 
> ---
> 
> ## **5.5 What Pricing Achieves**
> 
> * Positioning, Differentiation, Trial, Share stealing, Barriers to entry, Accelerating purchase cycles
> 
> ---
