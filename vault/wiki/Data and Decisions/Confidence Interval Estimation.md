---
title: "Confidence Interval Estimation"
course: Data and Decisions
sources:
  - "raw/data-and-decisions-cheat-sheet.md#Confidence Interval"
source_ids:
  - data-and-decisions-cheat-sheet#confidence-interval
key_terms: ["Population Parameter", "Sample Mean", "T-distribution", "Margin of Error", "Degrees of Freedom", "Standard Error"]
generated_by: mlx-community/gemma-4-e4b-it-4bit
ingested: 2026-09-22
reviewed: false
---
# Confidence Interval Estimation

A confidence interval provides a range within which the true population mean is likely to lie, based on sample data. It quantifies the uncertainty regarding unknown population parameters.

## Key points

- It is a range intended to hold the population mean with a specified degree of confidence.
- A Type I error occurs if the population mean falls outside the calculated interval.
- When population parameters are unknown, the t-critical value is used instead of the Z-score, leading to wider intervals.
- The interval can be calculated as: sample mean $\pm$ t-distribution $\times$ SE.
- Degrees of freedom (DF) are calculated as $n-1$.
- The T-distribution critical value can be found using $\text{T.INV}(\text{probability or } \alpha/2, \text{DF})$.

## Related notes

- [[Statistical Sampling Methods]]: Applies sampling methods to ensure the sample supports the confidence interval estimate.

## Sources

- [data-and-decisions-cheat-sheet.md › Confidence Interval](../../raw/data-and-decisions-cheat-sheet.md)
