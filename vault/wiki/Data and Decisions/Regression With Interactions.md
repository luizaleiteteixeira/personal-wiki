---
title: "Regression With Interactions"
course: Data and Decisions
sources:
  - "raw/data-and-decisions-cheat-sheet.md#Regression With Interactions"
source_ids:
  - data-and-decisions-cheat-sheet#regression-with-interactions
key_terms: ["Regression", "Dummy Variable", "Interaction Term", "Slope", "Intercept"]
generated_by: mlx-community/gemma-4-e4b-it-4bit
ingested: 2026-09-22
reviewed: false
---
# Regression With Interactions

This method involves including interaction terms in a regression model to analyze differences between groups. It allows for different intercepts and slopes depending on the group variable.

## Key points

- The model includes a constant, a group dummy variable, a main effect variable, and an interaction term.
- When the dummy variable is 0 (control group), the intercept is B0 and the slope is B2.
- When the dummy variable is 1 (treatment group), the intercept is B0+B1 and the slope is B2+B3.
- The treatment effect is represented by the coefficient B1.
- The slopes for the two scenarios are different if B3 is non-zero.
- The treatment effect can also be calculated as the difference in Y between the treatment and control groups.

## Related notes

- [[Multivariate Regression Analysis]]: Extends interaction analysis by modeling slopes influenced by multiple predictors simultaneously.
- [[Linear Regression Model]]: Extends the basic linear model by allowing group-specific intercepts and slopes.
- [[Dummy Variables for Categorical Data]]: Applies dummy variables to model group differences when including interaction terms.

## Sources

- [data-and-decisions-cheat-sheet.md › Regression With Interactions](../../raw/data-and-decisions-cheat-sheet.md)
