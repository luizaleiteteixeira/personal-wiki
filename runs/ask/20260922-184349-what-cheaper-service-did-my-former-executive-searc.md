# Ask: What cheaper service did my former executive search firm create so that startups could afford to work with us?

- Model: `mlx-community/gemma-4-e4b-it-4bit` (4-bit (MLX)), runtime mlx-vlm 0.7.2, mlx 0.32.2, execution: **local**
- Embeddings: `mlx-community/all-MiniLM-L6-v2-4bit`
- Citation check: **answered_with_citations**, weakly supported sentences: 0
- Generation: 7.7 s (steps [4.65, 3.05]), 1565 prompt tokens, 157 output tokens, MLX peak memory 5.87 GB

## Answer

My former executive search firm introduced a service that used "third-degree pricing discrimination based on company size and segment" [S2]. This meant that "Startups and digital firms paid lower fees, while large listed companies paid more" [S2]. This allowed "low type” clients, like startups, to afford the lower-priced version and start working with us [S1].

## Citations

- [S1] `raw/micro-examples-in-the-wild-4.md › Examples in the Wild 4`
- [S2] `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`

## Step 1: verified quotes

- [S2] `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`: "To address this, we introduced third-degree pricing discrimination based on company size and segment."
- [S2] `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`: "Startups and digital firms paid lower fees, while large listed companies paid more."
- [S1] `raw/micro-examples-in-the-wild-4.md › Examples in the Wild 4`: "while "low type” clients, like startups, started to work with us as they could now afford the lower-priced version."

Rejected quotes:
- none

## Support check

- none

## Retrieved passages

**[S1]** `raw/micro-examples-in-the-wild-4.md › Examples in the Wild 4`  (fused score 0.0328, cosine 0.495, bm25 27.46)

> This is an example of versioning in second-degree price discrimination. It was profitable because the "high type” clients, such as large corporations, had a higher willingness to pay for the upgrade (comprehensive service), while "low type” clients, like startups, started to work with us as they could now afford the lower-priced version. Clients revealed their willingness to pay during early discussions by selecting between packages, allowing us to expand our customer base and increase revenue without openly charging different prices for the same service.
> 
> **Word count: 185**

**[S2]** `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`  (fused score 0.0325, cosine 0.516, bm25 14.59)

> When I joined Egon Zehnder (EZ), their services had a single price across all clients. We soon realized that smaller companies, like startups, could not afford the full fee asked, while listed clients were less sensitive to price changes. To address this, we introduced third-degree pricing discrimination based on company size and segment. Startups and digital firms paid lower fees, while large listed companies paid more. This allowed EZ to win projects with elastic clients, while capturing additional revenue from less price-sensitive ones.

**[S3]** `raw/micro-examples-in-the-wild-2.md › Examples in the Wild 2`  (fused score 0.0323, cosine 0.460, bm25 22.00)

> I used to work for Egon Zehnder, a leadership advisory firm focused on executive search. I remember how hard it was to price a project, especially because it was difficult to measure the marginal cost of a search. 
> 
> "Should we accept this project?" was a frequent discussion.

**[S4]** `raw/micro-examples-in-the-wild-3.md › Examples in the Wild 3`  (fused score 0.0304, cosine 0.409, bm25 9.03)

> The conditions for segment pricing were present. First, there was heterogeneity in willingness to pay: startups faced budget constraints while corporations were open to paying higher fees. Second, we could identify “groups” using public information such as size, investments, and financial reports. Third, we could easily separate these segments in our pricing model, ensuring each one was charged appropriately.
> 
> The main threats are customer anger and competition. Some clients realized they were being charged different prices, which risked damaging trust. In addition, competitors could win projects by continuing to offer uniform rates to large corporations, which might force EZ to reconsider our pricing strategy. 
> 
> Still, segmentation expanded EZ’s client base and increased revenue overall.
> 
> **Word count: 197**

**[S5]** `raw/buscomm-case-3-west-side-united.md › Buscomm Case 3 West Side United`  (fused score 0.0271, cosine 0.384, bm25 6.11)

> Gaps: The structure is not fully stable yet, because it still depends a lot on funding, volunteers, and on how committed the hospitals and their leaders are. I also think they need to prioritize better, since they are trying to tackle very big and structural problems while still being a small organization.
> 
> Despite the gaps, I would fund the program, as I truly believe in their mission. They have shown that they can generate great impact and they have the potential to continue growing and improving.
> 
> **3) How well did Ansell and colleagues assemble a coalition and turn it into an organization? What vulnerabilities or gaps could interfere with the ability of WSU to continue its work?**

**[S6]** `raw/marketing-nike-case.md › Case`  (fused score 0.0259, cosine 0.372, bm25 4.85)

> **Nike’s Consumer Direct Offense Strategy: A Hit or a Miss?**
> 
> **Luiza Leite Teixeira**
> 
> **The problem and key issue to be addressed:**
> 
> In recent years, Nike has focused on its DTC strategy through initiatives like Consumer Direct Offense and Consumer Direct Acceleration. These programs increased brand control, consumer connection, loyalty, and digital engagement, with DTC now representing 44% of revenue. However, this brought new challenges: inventory accumulation of USD 8.5B, margin decline from 46 to 43.5% in FY2023, a 16% decline in net income, and more operational complexity from managing a large network of owned stores, apps, and logistics. At the same time, competitors such as On and Hoka captured Nike’s former shelf space and community presence in multi-brand retail.
