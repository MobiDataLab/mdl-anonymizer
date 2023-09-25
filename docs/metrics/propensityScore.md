# Propensity Score

In statistics, propensity score matching is a method commonly used in inference studies to compare outcomes among subjects that received a treatment, policy, or other intervention versus those that do not. To use Propensity score as a measure of utility, we need to train a model to estimate group membership between original and transformed datasets (e.g., anonymized or synthetic data). If original and anonymized datasets cannot be distinguished (small distinguishability score), then the utility of the anonymous data is high. 

Unlike RMSE metric, the propensity score is a data-agnostic utility metric that does not require a specific distance calculation for the specific data type. In addition, the propensity score is sensitive to anonymization via suppression of records because it results in an unbalanced input data for the model. On the other hand, the choice of the model for the propensity score calculation might influence the utility estimation of the anonymized data. With this in mind, logistic regression models are commonly used.

## Specific parameters

- tiles_size (int, optional, default: 200): Size of the squared tessellation (in meters)
- time_interval (int, optional, default: None): Consider the temporal component, size of every time interval (in seconds)
- seed (int, optional, default: None): Seed for the random process
