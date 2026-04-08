---
name: data-analysis
description: Use when analyzing data, creating visualizations, or extracting insights -- covers statistical methodology, pandas patterns, data cleaning, visualization best practices, and insight presentation
---

# Data Analysis

When helping with data analysis, follow this methodology to ensure statistical rigor, clear visualizations, and actionable insights.

## Core Concepts

### Descriptive Statistics

**Measures of Central Tendency**
- **Mean**: Average (sum / count). Use for symmetric distributions. Sensitive to outliers.
- **Median**: Middle value when sorted. Use for skewed distributions (income, house prices). Robust to outliers.
- **Mode**: Most frequent value. Use for categorical data.

**Measures of Spread**
- **Range**: Max - Min. Simple but misleading with outliers.
- **Standard Deviation**: Average distance from mean. 68% within 1 SD, 95% within 2 SD, 99.7% within 3 SD.
- **Variance**: Standard deviation squared. Less interpretable but mathematically useful.
- **Interquartile Range (IQR)**: Q3 - Q1 (middle 50%). Robust to outliers.

**Example**
```
Dataset: [10, 12, 12, 13, 15, 17, 100]

Mean: 25.6 (skewed by outlier 100)
Median: 13 (middle value, better representation)
Mode: 12 (appears twice)
Range: 90 (100 - 10)
Std Dev: 31.5 (high due to outlier)
IQR: 5 (Q3=16, Q1=11, ignores outlier)

Conclusion: Median + IQR better summarize this data (outlier present).
```

### Correlation Analysis

**Pearson Correlation (r)**
- Measures linear relationship between two variables
- Range: -1 (perfect negative) to +1 (perfect positive)
- Interpretation: |r| > 0.7 strong, 0.4-0.7 moderate, < 0.4 weak

**Correlation does NOT equal causation.**
- Example: Ice cream sales correlate with drowning deaths
- Hidden factor: Summer (hot weather causes both)
- Never assume X causes Y from correlation alone

**Scatterplot Interpretation**
```
Positive correlation: Points trend upward (r > 0)
Negative correlation: Points trend downward (r < 0)
No correlation: Random scatter (r ~ 0)
Non-linear: Curved pattern (Pearson r may not apply)
```

### Regression Basics

**Simple Linear Regression**
- Model: y = mx + b
- Predicts outcome (y) based on one input (x)

**R-Squared (R2)**
- Measures how well model fits data (0-100%)
- R2 = 0.85 means model explains 85% of variance
- Higher = better fit (but watch for overfitting)

**Residuals**
- Residual = Actual value - Predicted value
- Check residual plot (should be random, not patterned)
- Pattern in residuals = model is missing something

### Outlier Detection

**Methods**
1. **Z-Score**: Outlier if |z| > 3. Formula: z = (x - mean) / std_dev
2. **IQR Method**: Outlier if x < Q1 - 1.5*IQR or x > Q3 + 1.5*IQR
3. **Visual**: Boxplot, scatterplot (obvious extremes)

**Handling Outliers**
- Investigate first: Is it error (typo) or real (rare event)?
- Remove if: Data entry error, measurement error
- Keep if: Real extreme value (e.g., billionaire in income data)
- Transform if: Log transform reduces outlier impact

### Trend Analysis

**Types of Trends**
- **Linear**: Steady increase/decrease (straight line)
- **Exponential**: Accelerating growth (hockey stick)
- **Logarithmic**: Fast initial growth, then flattens
- **Cyclical**: Repeating pattern (seasonal sales)
- **Random**: No discernible pattern

**Moving Average**: Smooths noisy data to reveal underlying trend. Example: 7-day moving average for daily stock prices.

**Year-Over-Year (YoY) Comparison**: Compare same period in different years to remove seasonality. Better than month-over-month for seasonal businesses.

## Patterns and Procedures

### Pandas Data Analysis Workflow

```python
import pandas as pd
import numpy as np

# 1. Load data
df = pd.read_csv('data.csv')

# 2. Initial exploration
df.head()       # First 5 rows
df.info()       # Column types, null counts
df.describe()   # Summary stats

# 3. Clean data
df.dropna()                                # Remove missing values
df['column'] = df['column'].fillna(0)      # Fill nulls with 0
df.drop_duplicates()                       # Remove duplicate rows

# 4. Filter/subset
df[df['age'] > 30]                         # Rows where age > 30
df[['name', 'age']]                        # Select specific columns
df.loc[0:5, 'name']                        # Rows 0-5, column 'name'

# 5. Transform
df['new_col'] = df['col1'] + df['col2']    # Create column
df['log_price'] = np.log(df['price'])       # Log transform
df.groupby('category')['sales'].sum()       # Group by and aggregate

# 6. Analyze
df['sales'].mean()     # Mean
df['sales'].median()   # Median
df['sales'].std()      # Standard deviation
df.corr()              # Correlation matrix

# 7. Visualize (with matplotlib or seaborn)
df['sales'].hist()                           # Histogram
df.plot(x='date', y='sales')                # Line chart
df.boxplot(column='price', by='category')   # Box plot
```

### Statistical Analysis Process

```
1. Define question:
   "Is there a relationship between ad spend and sales?"

2. Collect data:
   - Ensure sufficient sample size (n > 30 for most stats)
   - Check data quality (missing values? outliers?)

3. Explore data:
   - Summary stats (mean, median, std dev)
   - Visualize distributions (histogram, boxplot)
   - Check for outliers

4. Run analysis:
   - Correlation: df.corr() or scipy.stats.pearsonr()
   - Regression: sklearn LinearRegression or statsmodels
   - T-test: scipy.stats.ttest_ind() for group comparison

5. Interpret results:
   - Check p-value (< 0.05 = statistically significant)
   - Check effect size (is difference meaningful?)
   - Check R2 (how much variance explained?)

6. Communicate findings:
   - Visualization (chart that tells the story)
   - One-sentence insight: "Each $1k in ad spend increases sales by $3k (R2=0.72)"
   - Caveat: "Correlation, not causation; other factors may contribute"
```

### Outlier Investigation Workflow

```
1. Detect outliers:
   - IQR method: x < Q1 - 1.5*IQR or x > Q3 + 1.5*IQR
   - Z-score: |z| > 3
   - Visual: Boxplot shows dots beyond whiskers

2. Investigate cause:
   - Data entry error? (typo: 1000 instead of 100)
   - Measurement error? (faulty sensor)
   - Real extreme value? (celebrity, rare event)

3. Decision:
   - If error: Correct or remove
   - If real but rare: Keep (document as outlier)
   - If distorts analysis: Transform (log) or use robust stats (median)

4. Document:
   - Note which values were outliers
   - Explain why you kept or removed them
   - Run analysis both ways (with and without outliers)
```

## Data Visualization Best Practices

### Choosing the Right Chart

| Chart Type | Use When | Example |
|-----------|----------|---------|
| **Line chart** | Trends over time | Stock prices, website traffic |
| **Bar chart** | Comparisons across categories | Sales by region |
| **Histogram** | Distribution of single variable | Age distribution |
| **Scatterplot** | Relationship between two variables | Height vs weight |
| **Boxplot** | Compare distributions across groups | Salary by department |
| **Heatmap** | Correlation matrix | Multiple variable relationships |

### Design Principles

- Start y-axis at 0 (don't exaggerate differences)
- Label axes clearly (units, what each axis represents)
- Use color purposefully (highlight key data, not decoration)
- Avoid 3D charts (distorts perception, hard to read)
- Limit to 5-7 categories (too many = cluttered)
- Add title that tells the insight ("Sales increased 20% YoY", not "Sales Chart")

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| **Mean for skewed data** | Mean = $500k, but median = $50k (billionaire skew) | Use median for skewed distributions |
| **Correlation = Causation** | "Ice cream causes drowning" | Check for confounding variables |
| **Small sample size** | n=10, conclude "5% difference" | Minimum n=30, use power analysis |
| **P-Hacking** | Test 20 hypotheses, find 1 with p<0.05 | Pre-register hypothesis, Bonferroni correction |
| **Cherry-picking time periods** | "Sales up 50% last month!" (down 20% overall) | Show full time series, use YoY |
| **Ignoring outliers** | Mean of [10, 12, 13, 15, 1000] = 210 | Investigate outliers, use median or remove if errors |

## Quick Reference

### Statistical Tests Quick Guide

```
Compare two groups:
- T-test: scipy.stats.ttest_ind(group1, group2)
- Use when: Normal distribution, continuous data

Compare multiple groups:
- ANOVA: scipy.stats.f_oneway(g1, g2, g3)
- Use when: 3+ groups, normal distribution

Correlation:
- Pearson: scipy.stats.pearsonr(x, y)
- Use when: Linear relationship, continuous data

Non-parametric (non-normal data):
- Mann-Whitney U: scipy.stats.mannwhitneyu(g1, g2)
- Spearman correlation: scipy.stats.spearmanr(x, y)
```

### Visualization Libraries

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Matplotlib (basic)
plt.plot(x, y)                 # Line chart
plt.bar(categories, values)    # Bar chart
plt.hist(data)                 # Histogram
plt.scatter(x, y)              # Scatterplot

# Seaborn (advanced)
sns.lineplot(data=df, x='date', y='sales')
sns.barplot(data=df, x='category', y='sales')
sns.histplot(data=df, x='age', bins=20)
sns.scatterplot(data=df, x='x', y='y', hue='category')
sns.boxplot(data=df, x='category', y='price')
sns.heatmap(df.corr(), annot=True)    # Correlation heatmap
```

### Interpreting Correlation Coefficients

```
r = 1.0:          Perfect positive (x up -> y up exactly)
r = 0.7 to 0.9:   Strong positive
r = 0.4 to 0.7:   Moderate positive
r = 0.1 to 0.4:   Weak positive
r = 0.0:          No correlation
r = -0.1 to -0.4: Weak negative
r = -0.4 to -0.7: Moderate negative
r = -0.7 to -0.9: Strong negative
r = -1.0:         Perfect negative (x up -> y down exactly)
```

## Checklists

### Starting Data Analysis
- [ ] Load data (CSV, Excel, database)
- [ ] Check shape (rows, columns)
- [ ] View first/last rows (df.head(), df.tail())
- [ ] Check data types (df.dtypes)
- [ ] Check for missing values (df.info(), df.isnull().sum())
- [ ] Summary statistics (df.describe())

### Cleaning Data
- [ ] Handle missing values (drop, fill, or impute)
- [ ] Remove duplicates (df.drop_duplicates())
- [ ] Fix data types (convert strings to numbers, dates)
- [ ] Trim whitespace (str.strip() for text columns)
- [ ] Detect outliers (boxplot, z-score, IQR method)
- [ ] Investigate outliers (error vs real extreme value)

### Exploratory Analysis
- [ ] Calculate central tendency (mean, median, mode)
- [ ] Calculate spread (std dev, IQR, range)
- [ ] Visualize distributions (histogram, boxplot)
- [ ] Check for skewness (mean vs median, histogram shape)
- [ ] Correlation matrix (df.corr())
- [ ] Scatterplots for key relationships

### Statistical Analysis
- [ ] Define hypothesis (specific question to answer)
- [ ] Choose appropriate test (t-test, ANOVA, correlation, regression)
- [ ] Check assumptions (normality, sample size)
- [ ] Run test (scipy.stats or statsmodels)
- [ ] Check p-value (< 0.05 = significant)
- [ ] Check effect size (R2, correlation coefficient)
- [ ] Interpret in context (practical significance)

### Visualization
- [ ] Choose right chart type (line, bar, scatter, box, heatmap)
- [ ] Label axes clearly (include units)
- [ ] Add title that conveys insight (not generic "Chart")
- [ ] Start y-axis at 0 (unless good reason not to)
- [ ] Use color purposefully (highlight key data)
- [ ] Simplify (remove clutter, limit categories to 5-7)

### Communicating Results
- [ ] One-sentence key insight (what's the main takeaway?)
- [ ] Supporting evidence (statistics, visualization)
- [ ] Caveats (limitations, assumptions, correlation does not equal causation)
- [ ] Recommendations (actionable next steps based on analysis)
- [ ] Document methodology (how you cleaned, analyzed, visualized)
