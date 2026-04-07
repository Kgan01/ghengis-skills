# Data Analysis -- Evaluation

## TC-1: Skewed Distribution Summary
- **prompt:** "I have income data: [25k, 30k, 32k, 35k, 40k, 42k, 45k, 50k, 2M]. What's the best way to summarize it?"
- **context:** Dataset contains a clear outlier (2M) that will skew the mean. User wants a representative summary.
- **assertions:**
  - Recommends median over mean as the central tendency measure due to the outlier
  - Calculates or explains the mean is heavily skewed by the 2M value
  - Suggests IQR over standard deviation for spread measurement
  - Identifies the 2M value as an outlier using IQR method or z-score
  - Recommends investigating whether the outlier is a data entry error or a real value
- **passing_grade:** 4/5 assertions must pass

## TC-2: Correlation Analysis with Caveat
- **prompt:** "My dataset shows ice cream sales and sunburn rates have r=0.87. Does ice cream cause sunburns?"
- **context:** User has a strong positive correlation and is tempted to infer causation.
- **assertions:**
  - Identifies r=0.87 as a strong positive correlation
  - Explicitly states correlation does not equal causation
  - Suggests a confounding variable (e.g., hot weather/summer driving both)
  - Recommends further investigation (controlled experiment, regression with confounders)
- **passing_grade:** 3/4 assertions must pass

## TC-3: Choose the Right Visualization
- **prompt:** "I have monthly sales data for 3 product categories over 2 years. What chart should I use?"
- **context:** Time-series data across categories. User needs guidance on visualization type.
- **assertions:**
  - Recommends a line chart for trends over time
  - Suggests using different colors or lines per category (not a single aggregated line)
  - Mentions labeling axes clearly with units (month/year on x-axis, sales on y-axis)
  - Advises the chart title should convey the insight, not just say "Sales Chart"
  - Limits categories to a reasonable number (3 is fine; warns if more than 5-7)
- **passing_grade:** 3/5 assertions must pass

## TC-4: Pandas Data Cleaning Workflow
- **prompt:** "I loaded a CSV with 50k rows. It has missing values, duplicates, and some columns are strings that should be numbers. Walk me through cleaning it."
- **context:** Raw messy dataset. User needs a structured cleaning workflow.
- **assertions:**
  - Starts with exploration: `df.info()`, `df.describe()`, `df.isnull().sum()`
  - Addresses missing values (drop, fill, or impute with rationale for each)
  - Addresses duplicates with `df.drop_duplicates()`
  - Addresses type conversion (strings to numeric, mentioning `pd.to_numeric` or `astype`)
  - Mentions outlier detection as a cleaning step (boxplot, z-score, or IQR)
- **passing_grade:** 4/5 assertions must pass

## TC-5: Small Sample Size Warning
- **prompt:** "I surveyed 8 people and found a 5% difference between groups A and B. Is this statistically significant?"
- **context:** User has a very small sample and is trying to draw conclusions.
- **assertions:**
  - Warns that n=8 is too small for reliable statistical conclusions
  - Mentions minimum sample size guidance (n>30 for most tests)
  - Does not declare the 5% difference as statistically significant
  - Suggests collecting more data or using power analysis to determine needed sample size
- **passing_grade:** 3/4 assertions must pass
