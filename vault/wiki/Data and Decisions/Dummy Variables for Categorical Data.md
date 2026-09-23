---
title: "Dummy Variables for Categorical Data"
course: Data and Decisions
sources:
  - "raw/data-and-decisions-cheat-sheet.md#Categorical Variables"
source_ids:
  - data-and-decisions-cheat-sheet#categorical-variables
key_terms: ["Dummy Variable", "Control Group", "Treatment Effect", "Regression", "Base Category"]
generated_by: mlx-community/gemma-4-e4b-it-4bit
ingested: 2026-09-22
reviewed: false
---
# Dummy Variables for Categorical Data

Categorical variables can be converted into dummy or indicator variables, typically taking values of 0 or 1. This allows for regression analysis where one group serves as the control group against which others are compared.

## Key points

- A dummy variable takes a value of 1 or 0, where 0 is usually the control group.
- For $k$ categories, $k-1$ binary variables must be created, omitting one as the base category.
- The coefficient for a treatment group represents the average effect of that treatment relative to the control group.
- If all coefficients are significant, both treatments have a statistically significant effect on the outcome variable ($Y$).
- The difference between two treatment effects can be calculated by subtracting their respective coefficients.

## Related notes

- [[Regression With Interactions]]: Extends dummy variables by modeling group-specific slopes and intercepts through interaction terms.

## Sources

- [data-and-decisions-cheat-sheet.md › Categorical Variables](../../raw/data-and-decisions-cheat-sheet.md)
