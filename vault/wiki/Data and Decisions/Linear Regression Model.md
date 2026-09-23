---
title: "Linear Regression Model"
course: Data and Decisions
sources:
  - "raw/data-and-decisions-cheat-sheet.md#Linear Regression Model"
source_ids:
  - data-and-decisions-cheat-sheet#linear-regression-model
key_terms: ["Intercept", "Slope", "Residual", "$R^2$", "T-stat", "Prediction Interval"]
generated_by: mlx-community/gemma-4-e4b-it-4bit
ingested: 2026-09-22
reviewed: false
---
# Linear Regression Model

Linear regression models the linear relationship between two variables, predicting one variable (Y) as a function of another (X). The model uses coefficients ($\beta_0$ and $\beta_1$) to quantify this relationship, assuming certain conditions regarding the errors are met.

## Key points

- The population model is $Y = \beta_0 + \beta_1 * X$, and the estimated model is $Y^ = b_0 + b_1 * X + \varepsilon$.
- $b_0$ is the intercept, representing the portion of $Y$ present when $X$ is zero.
- $b_1$ is the slope, representing the change in $Y$ associated with a one-unit change in $X$.
- Residual ($\varepsilon$) is the prediction error, representing what the model fails to explain.
- $R^2$ indicates the percentage of variation in $Y$ explained by $X$.
- Statistical significance is tested using the T-statistic and P-value against a chosen alpha ($\alpha$).
- Prediction intervals provide a range of plausible values for $Y$ given a specific $X$.

## Related notes

- [[Regression With Interactions]]: Extends linear models by allowing group differences in intercepts and slopes.
- [[Multivariate Regression Analysis]]: Extends linear models by including multiple predictors to account for variable influences.
- [[Estimating Asset Beta]]: Applies linear regression to estimate unlevered asset beta from market data.

## Sources

- [data-and-decisions-cheat-sheet.md › Linear Regression Model](../../raw/data-and-decisions-cheat-sheet.md)
