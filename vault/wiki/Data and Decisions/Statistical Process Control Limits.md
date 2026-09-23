---
title: "Statistical Process Control Limits"
course: Data and Decisions
sources:
  - "raw/data-and-decisions-cheat-sheet.md#Control Limits"
source_ids:
  - data-and-decisions-cheat-sheet#control-limits
key_terms: ["Population Parameters", "Type I Error", "Type II Error", "Control Limits", "Z-statistic", "$\\alpha$"]
generated_by: mlx-community/gemma-4-e4b-it-4bit
ingested: 2026-09-22
reviewed: false
---
# Statistical Process Control Limits

Control limits are used to check if a process is functioning correctly when population parameters are known. They help in monitoring a process and managing the risk of making incorrect decisions.

## Key points

- Type I error is a false positive, where action is taken when none is needed.
- Type II error is a false negative, where action is needed but not taken.
- A larger $\alpha$ leads to a smaller control limit, increasing Type I errors.
- The upper limit is calculated as $\mu + L$, and the lower limit is $\mu - L$.
- $L$ is determined by $Z \times SE$, where $Z$ is the Z-statistic.
- The Z-score corresponds to the acceptable probability of a Type I error ($\alpha$).

## Related notes

- _No closely related notes._

## Sources

- [data-and-decisions-cheat-sheet.md › Control Limits](../../raw/data-and-decisions-cheat-sheet.md)
