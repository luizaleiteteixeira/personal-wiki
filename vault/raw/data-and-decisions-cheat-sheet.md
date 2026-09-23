# Cheat sheet D&D

SAMPLE
We use the sample (subset of the collection of interest) data (statistics) to make an educated guess (inference) about the parameter (characteristics of population), because census are hard and expensive

Types: sampling frame has to be representative
Simple Random Sampling: Gold standard (coin, excel)
(1) =RAND(); (2) Copy values only; (3) Sort and pick X first
Stratified Sampling: SRS for each subsets/group. Proportional or non-prop
(1) Select characteristic; (2) Countif; (3) Select a sample for each; (4) =RAND(); (5) Copy values only; (6) filter charac. and rand number
Cluster Sampling: SRS for each randomly selected group if all groups are homogeneous.
Bias: sample is not representative of the population
Sampling frame: not representative of the population (over indexing in one specific characteristic that not everyone has);
Self selection: people decide whether to participate and they are different from the ones who don't, extreme views/different characteristics;
Survivorship: only people who survived a certain process, and has certain long-living characteristics, hides failures or those who dropped out;
Convenience sampling: easiest to reach, similar to one another (social or geographic circle, not the full population);
Measurement: observer effect, questions poorly worded, the scale doesn’t fit the context, or respondents don’t give truthful answers - over or under-reported
Mitigation: professional recruiting, recruiting (payment, relationship), poll of polls average, sensibility / modeling the bias
Law of Large Numbers: As sample size grows, the sample mean tends to become closer to the true mean
Central Limit Theorem: with a random sample, and a large enough sample size, the distribution of the sample mean is normally distributed with a mean equal to the population mean (this is how we get an unbiased estimate), and standard deviation equal to the standard error. Mean equals sum divided by n. Applies to any type of distribution.
Conditions: has to be big enough → N > 10 * |K4|
K4 = kurtosis - measures if there are outliers. =0 for normal data
=KURT (sample values)

CONTROL LIMITS
We know population parameters → check if process is working properly
Possible errors: Type I: false positive (took action when no action was needed) - usually given as ɑ; Type II: false negative (not taking action when it was needed)
Larger ɑ → control limit smaller → stopping machine all the time. A lot of Type I error, but limited type 2. When larger control limit, few Type I but more Type II. If we increase CL → reduce Type I error
Steps: (1) population parameters; (2) run a sample; (3) calculate control limits; (4) decide if follow or not; (5) analyze error
Upper limit = μ + L
Lower limit = μ - L
L = Z * SE
Z = Z-stat - score number based on your
on ɑ (% ok with type I error) - search in the two-sided or ɑ/2 in one-tail
Z → =NORM.S.INV(ɑ/2)
Type I error: NORM.DIST(μ-L, μ, σ, TRUE) * 2

CONFIDENCE INTERVAL
We don't know population parameters → range that should hold the population mean with a certain confidence based on a sample
X% confident that the value of the population/ true mean is between {a, b}. Type I error is when the population mean is not in the interval.
Larger ɑ, larger CI, less precise estimate of the population parameter
As we don't know pop. parameters, we have to pay a penalty by using t-critical value instead of Z → confidence interval becomes wider, less precise.
Increase in n brings t-drist closer to normal distribution, and values become closer to the truth.
CI more narrowed (DF increases → decrease t-dist + SE can decrease)
(1) Calculate T-distribution / T critical value:
 =T.INV (probability or α/2, DF)
Consider absolute value
Probability = ɑ / 2
If only Z-score, use Z-table to find it
Degrees of freedom (DF) = n-1
(2) CI = sample mean +- t-distribution x SE
Using margin of error (similar outcome, but less precise)
Mean: sample average ± 2s/√n
Proportion: 2√((p(1-p))/n)

HYPOTHESIS TESTING
No info on population, you analyze sample to see where is pointing more
Null hypothesis (H0): status quo, where you are.
Alternative hypothesis (Ha): goes in another direction, what we want to prove (take action)
Two-tail = more conservative test
(1) State H0 and Ha
(2) T-statistics = (sample average - k) / SE
(3) Find P-value associate with this t
TWO TAIL:  =t.dist.2T (abs(t-stat), DF)
RIGHT TAIL:  =t.dist.RT (t-stat, DF)
LEFT TAIL:  =t.dist (t-stat, DF, TRUE)
Probability of seeing this number (or more extreme) if the null hypothesis is true. Shows if the sample is far enough from the population average
(4) Reject the null if p-value < ɑ. Fail to reject if p-value > ɑ
The higher the ɑ more in favor of your alternative, higher the chance of Ha being right
The bigger t-stat, the more the data is pointing to alternative hypothesis
If proportion: use the null hypothesis to calculate Z-score = (population average - number we want to see if it's high/low/different) / SE

A/B TESTING / TWO-SAMPLE TESTING
Randomized Control Trial (RCT) - Procedure that uses randomization of treatment and control status to produce data that reveal causation
Sample size condition must be met by both samples
Outcome = b0 + b1 * treatment (group B)
Hypothesis testing - two sample t-test to choose between options
H0 - suggest the status quo / control group / simpler (μA - μB = >= or <= D0)
The order matters! What are you testing? If B is higher, H0 is μB - μA <= 0
Ha - suggests the other option, that requires change or more money
D0 = difference you want to go with alternative
CI are less accurate/specific, but can be used to reject the null hypothesis if the D0 is not in the interval
Condition: characteristics of control and treatment groups have to be balanced, so they only differ in what you want to test → randomization to avoid bias
Problem: expensive, need more than one experiment to be valid, can haven outliers (always plot the data)
As you don't have the population parameters, you use statistics
State the hypothesis (one tail or two tail?)
(1) Run t-test
Data analysis → t-test: two sample assuming equal variance
Select both samples, hypothesis mean difference = D0, ɑ
One tail, order does not matter, instead tells you if either strictly smaller
Option 2: T-stat = ((average A - average B) - k)/SE
SE of xa and xb = √(SEa2 + SEb2)
(2) Find p-value associate with this T-stat (as steps on HT)
TWO TAIL:  =t.dist.2T (t-stat, DF, TRUE)
RIGHT TAIL:  =t.dist.RT (t-stat, DF, TRUE)
LEFT TAIL:  =t.dist (t-stat, DF, TRUE)
DF = na + nb -2
(3) Conclusion
Reject the null if p-value < ɑ. Fail to reject if p-value > ɑ
Conclude that _ is statistically significantly OR  no statistical evidence that
As we are not 100% sure, we measure our uncertainty = Standard Error
SE = σ/√n (we can use s if we don't have sigma) or √p(1-p)/√n
Smaller the SE, more precision
Square root =SQRT (value); Standard deviation =STDEV (values)
If sample increases, SE decreases and CI becomes narrowed
How much variation we can expect - how far the sample average tends to be from the truth
Validity:
Internal: ability to identify the causal effect (the only difference between treatment and control groups is the treatment they receive). Otherwise: confounding factors. In the case of a demand function = yes. Proper experiment? Random, no bias, etc..
External: can generalize from your analysis to other contexts/scenarios
Statistics for samples:
Data analysis → descriptive statistics → select sample → click on summary statistics
If comparing samples: I don't know if they are statistically different, so we would have to run a regression or HT. With just the summary statistics, it’s hard to pin down the statistical significance of these differences.

-----

REGRESSION
LINEAR REGRESSION MODEL
Express linear relationship between two variables Y and X
Regress Y on X, Y as a function of X, how X predicts Y, impact of X on Y…
β0 and β1 - population, but we estimate with sample numbers. Conditions: errors are (1) independent, (2) normally distributed, (3) have identical variance
Y = β0 + β1 * X
Y^ = b0 + b1 * X + ɛ
y^ = predicted value given a value of X
Ɛ = prediction error, what is not explained by your model. Is the deviations around conditional mean (errors, shocks). Can be positive or negative but zero on average and normally distributed
b0 and b1 are the ones that minimize the sum of squared residuals
B0 = intercept, entry value → portion of y that is present for all values of x
B1 = slope → change in y associated with a one unit change in x, predicted change in the outcome when the explanatory variable changes by 1 unit. Not cause!
(1) Plot the data to see if it's linear
Change in Y has to be similar for all changes in X
Select Y and X → insert → chart: scatterplot
Click on the chart → chart design → add chart element → trendline - linear
Right click → add trendline → right click again → display equation and R2
(2) Run a regression
Data analysis → regression
(3) Interpretation / test the significance
Residual is what the model fails to explain. E = difference between the data and the line → e = y - yˆ.
Condition: the x variable and residual should not have a correlation (independent), residuals have to have a normal distribution and similar variances - linear model is appropriate and residual variation is random
Positive residual = over predicting / Negative = underpredicting
SE: measure of prediction error - how far the residuals are from the fitted line → what our model fails to explain
R-squared = predicted power:  % of variation in Y that is explained by X → what our model explains. Change in X explains R2% of the variation in Y.
For each coefficient:
T-stat has to be large (distance from my data to the null relativity to my error)
P-value has to be lower than ɑ to be statistically significant. A large p-value is imprecise and the number can be zero.
For each variable it runs a hypothesis testing (H0: B0 = 0 or Ha: B0 not 0). If P-value < ɑ, you reject the null that the coefficient is zero. If you fail to reject, the data can be 0
If you want to do another HT for B being another value - compete with t-stat (B - number you want to compare) / SE) and t-dist by hand based on the information you get from regression
Confidence interval (CI): 95% confident that the true effect of the treatment on Y  lies between __ and __. 95 out of 100 samples where we construct a 95% CI, the interval we get will contain the true coefficient.
(4) Prediction - putting X values to check what the Y is
Be careful with extrapolation! Avoid trying to project the data very far from your data, because the model cannot work well
Prediction interval = Klein Bridge: range of plausible/reasonable values for your Y when you X is __. Hold a fraction (usually 95%) of the values of the response y for a given value of x.
Upper → Y^ + 2*SE
Lower → Y^ - 2*SE
Y^ - estimated Y given the X.
Consider SE of the regression model

Adding more co-variates:
R2: always increase (mechanically) as add more explanatory power to the regression.
SE: good variables reduces the noise of regression, so lowers the SE of the regression and sometimes of the coefficients. If add useless, reduce DF and can increase SE.
Adjusted R2: may increase or decrease. Increases when the model explains more the variation of Y. Decreases when variables don't explain anything, they are not adding explanatory power. Makes sense to get a few out - the ones with high correlation, or that p-value is not significant.
Coefficient of one variable doesn’t change. It’s only affected if variables are correlated (omitted variable bias). Randomization ensures the treatment variables are statistically independent of other potential causes of outcome. Adding more co-variates will help increase precision of this estimate but will not change the estimate itself.
However, if you add an interaction variable, the coefficients won’t mean the same (and just part of the sample/population). So the coefficient will stay the same or decrease (as the new interaction will pick up the effect of the previous individual coefficient)

CATEGORICAL VARIABLES
Categorical variable will be a dummy/indicator variable with value 1 or 0. 0 will be the control group (usually status quo), and 1 will be the treatment
If not stated this way, create a dummy variable on Excel
ABC test: Group A = control. Group B = treatment B. Group C = treatment C
Y = B0 + B1 * treatment B + B2 * treatment C + Ɛ
(1) Create two dummies - one for treatment B (where A and C will be 0 and B will be 1 and one for treatment C (where A and B are 0 and C is 1)
=IF(celula="B",1,0) and =IF(celula="C",1,0)
(2) Run regression and interpret
 A → Y = B0. B → Y = B0+B1. C → Y = B0+B2
Treatment effect is B1 for B and B2 for C
Difference between B and C = B2-B1
If all coefficients are significant → both group B and group C treatments have a statistically significant effect on Y relative to group A.
Interpretation if you add other variables in addition to groups:
Y = b0 + b1*groupB + b2*groupC + b3*categoryB + b4*categoryC + b5*categoryD + e
B0 = average Y from control group who is also in the base variable
BGroup: average treatment effect of Treatment _ on Y relative to control group, controlling for variables / for any differences in Y among variable categories.
treatment effect for any product type,
BVariable: Each b is the difference in average Y between the category multiplying the coefficient and the base variable, controlling for treatment group
When creating dummy: omit one category (the “base category) and create (k-1) binary variables for the non-omitted categories
P-value: difference has statistic significance OR no evidence that Y varies by product type once the effect of the treatments is considered

REGRESSION WITH INTERACTIONS
(1) Prepare the data
Put columns of X variables in sequence
Choose control group (dummy = 0)
Create interaction variable (dummy * X) → yo avoid omitted variable bias
(2) Regression
Y = B0 + B1*dummy + B2*X + B3*dummy*X + Ɛ
Dummy = 0 → intercept = B0; slope = B2
Dummy = 1 → intercept = B0+B1; slope = B2+B3
Treatment effect = B1
Sensibility = slope. When p-value is large, the coefficient can be 0, which means that the slope/intercept of the function can be the same for both the scenarios
(3) Analysis
Treatment effect = Y for treatment - Y for control group
TIPS
Interpret the coefficients: state the coefficient, explain what it means. Explain if it's statistically significant.
Fit → explanatory power and statistically significance

MULTIVARIATE REGRESSIONS
Marginal regression: Slope also considers the impact of other Xs, so it can be a worse prediction model. - what we see in an one variable case
Partial regression: Slope considers only the impact of this variable, as the others are seen as constant. Relationship between X and Y controlling for other
Analysis for the model:
Significance F → p-value of the f-stat. If lower than ɑ, the model is statistically significant and has explanation power. If bigger: model is useless
Adjusted R-squared → Explanatory power of your model. It can penalize the model for having more regressors than the models
Check each variable p-value and coefficient
To interpret: B0: effect on Y when other variables are 0. Other B: difference on probability / effect/increase/decrease in Y conditional on all other X’s.

Omitted Variable Bias:
Wrongly attributing the effect of an omitted variable to another variable that is in the model - gives a misleading or incorrect model. To be an omitted variable - has to be correlated with both the Y and at least other X.
To estimate the effect: b~1 = b1 + b2 * correlation (var1, var2)
B~1 is what you actually estimated
B1 = direct effect (perfect model)
B2 = indirect effect (perfect model)
If correlation is 0 or b2 is zero, there is no OVB (b~1 = b1)
How to mess regression / have a worse model:
Collinearity: high correlation (>95%) between variables, that end up not explaining the model anymore. Adjusted R-squared doesn't change much.
Overfitting: random variables that actually don't explain. Add new data points
Lack of power: not statistically significant (no relationship or small n). To improve: increase sample size (number of people or period evaluated)
SE increases when adding a variable
Slope changes a lot when you add/drop variables
Direction of bias
Upward: overestimating the effect of your variable. b~1 > b1
Downward: underestimating. b~1 < b1
Smokin band
Check as you Go
SAMPLE
CI
HT
REGRESSION
