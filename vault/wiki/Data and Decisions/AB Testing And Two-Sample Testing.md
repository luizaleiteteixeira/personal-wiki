---
title: "AB Testing And Two-Sample Testing"
course: Data and Decisions
sources:
  - "raw/data-and-decisions-cheat-sheet.md#A/B Testing / Two-Sample Testing"
source_ids:
  - data-and-decisions-cheat-sheet#a-b-testing-two-sample-testing
key_terms: ["Randomized Control Trial", "Hypothesis Testing", "T-test", "Null Hypothesis", "Alpha ($\\alpha$)", "Degrees of Freedom"]
generated_by: mlx-community/gemma-4-e4b-it-4bit
ingested: 2026-09-22
reviewed: false
---
# AB Testing And Two-Sample Testing

A/B testing, or Randomized Control Trial (RCT), is a procedure using randomization to establish causation between treatments and control groups. Hypothesis testing, often involving a two-sample t-test, is used to compare outcomes between these groups.

## Key points

- RCT uses randomization of treatment and control status to reveal causation.
- Hypothesis testing compares options using a two-sample t-test.
- H0 suggests the status quo, while Ha suggests the alternative requiring change.
- The difference you want to go with the alternative is denoted as D0.
- To reject the null hypothesis, the p-value must be less than alpha ($\alpha$).
- Degrees of freedom (DF) are calculated as $n_a + n_b - 2$.
- Internal validity requires that the only difference between groups is the treatment received.

## Related notes

- [[Hypothesis Testing Procedure]]: Applies hypothesis testing to rigorously compare A/B test outcomes using statistical evidence.

## Sources

- [data-and-decisions-cheat-sheet.md › A/B Testing / Two-Sample Testing](../../raw/data-and-decisions-cheat-sheet.md)
