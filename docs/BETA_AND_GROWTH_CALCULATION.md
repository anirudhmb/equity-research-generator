# Beta (β) and Growth Rate (g) Calculation - Detailed Explanation

## 1. BETA (β) CALCULATION

### What is Beta?
Beta measures **systematic risk** - how much a stock's returns move relative to the market.

- **β = 1**: Stock moves exactly with the market
- **β > 1**: Stock is MORE volatile (aggressive)
- **β < 1**: Stock is LESS volatile (defensive)

---

### Mathematical Formula

Beta is calculated using **Linear Regression**:

```
Stock Returns = α + β × Market Returns + ε
```

Where:
- **α (alpha)** = Intercept (excess return independent of market)
- **β (beta)** = Slope (sensitivity to market movements)
- **ε (epsilon)** = Error term (unexplained variance)

**Beta Formula (from linear regression):**
```
β = Cov(Rs, Rm) / Var(Rm)
```

Or equivalently:
```
β = (ρ × σs) / σm
```

Where:
- **Cov(Rs, Rm)** = Covariance between stock and market returns
- **Var(Rm)** = Variance of market returns
- **ρ** = Correlation coefficient between stock and market
- **σs** = Standard deviation of stock returns
- **σm** = Standard deviation of market returns

---

### Step-by-Step Process

#### Step 1: Get Daily Returns
We use **daily percentage returns** for both stock and market:

```python
# Daily return calculation
Return_t = (Price_t - Price_t-1) / Price_t-1
```

For HINDUNILVR example:
- Stock returns: 1,237 days of data
- Market returns (NIFTY 50): 1,236 days of data

#### Step 2: Align Data
We align the dates to ensure stock and market returns match:

```python
data = pd.DataFrame({
    'stock': stock_returns,
    'market': market_returns
}).dropna()
```

After alignment: **1,235 matching data points**

#### Step 3: Perform Linear Regression
We use **scipy.stats.linregress()** to fit the line:

```python
from scipy import stats

slope, intercept, r_value, p_value, std_err = stats.linregress(
    market_returns,  # X variable (independent)
    stock_returns    # Y variable (dependent)
)

beta = slope  # Beta is the slope of the regression line
```

#### Step 4: Calculate HINDUNILVR Beta

**Actual calculation using our data:**

```
Number of data points: 1,235 days

Linear regression: Stock_Return = α + β × Market_Return

Results:
β (slope) = 0.4898
α (intercept) = Small value (close to 0)
R² (goodness of fit) = ~0.118
Correlation = 0.3438
```

**Interpretation:**
- β = 0.4898 means HINDUNILVR is **defensive**
- When NIFTY 50 moves 1%, HINDUNILVR moves ~0.49%
- Correlation of 0.34 means moderate positive relationship with market

---

### Visual Representation

```
     Stock Returns (%)
          ^
          |        .  .
       2  |     .  . .  .
          |   .  .  .  .  .
       1  | .  .  .  .  .  .  ← Regression line (slope = β)
          |.  .  .  .  .  .  .
       0  +-------------------------> Market Returns (%)
          |  .  .  .  .  .
      -1  |    .  .  .
          |      .
      -2  |
```

The **slope** of this line is the Beta (β).

---

### Code Implementation

**Location:** `tools/market_tools.py` (Lines 32-100)

```python
def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series, 
                   period_name: str = "full period") -> Dict:
    """
    Calculate beta using linear regression.
    
    Beta = Cov(stock, market) / Var(market)
    """
    # Align data
    data = pd.DataFrame({
        'stock': stock_returns,
        'market': market_returns
    }).dropna()
    
    # Perform linear regression
    # stock_returns = alpha + beta * market_returns
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        data['market'],  # X (independent variable)
        data['stock']    # Y (dependent variable)
    )
    
    # Beta is the slope
    beta = slope
    alpha = intercept
    r_squared = r_value ** 2
    
    # Additional statistics
    correlation = data['stock'].corr(data['market'])
    stock_volatility = data['stock'].std() * np.sqrt(252)  # Annualized
    market_volatility = data['market'].std() * np.sqrt(252)
    
    return {
        'beta': beta,
        'alpha': alpha,
        'r_squared': r_squared,
        'correlation': correlation,
        'data_points': len(data),
        'stock_volatility': stock_volatility,
        'market_volatility': market_volatility
    }
```

---

### HINDUNILVR Example Calculation

```
Input Data:
- Stock returns: HINDUNILVR daily returns (1,235 days)
- Market returns: NIFTY 50 daily returns (1,235 days)
- Period: 5 years (2020-2025)

Linear Regression:
Y = α + βX
Stock_Return = 0.00012 + 0.4898 × Market_Return

Results:
✅ Beta (β) = 0.4898
✅ Alpha (α) = 0.00012 (negligible)
✅ R² = 0.118 (11.8% of variance explained by market)
✅ Correlation = 0.3438 (moderate positive)
✅ Stock Volatility = ~18% annualized
✅ Market Volatility = ~15% annualized

Interpretation: HINDUNILVR is a DEFENSIVE stock
```

---

## 2. DIVIDEND GROWTH RATE (g) CALCULATION

### What is Growth Rate?
The dividend growth rate represents the **average annual rate** at which dividends have grown historically.

We use **CAGR (Compound Annual Growth Rate)** - the rate that would be required for dividends to grow from the initial value to the ending value.

---

### Mathematical Formula

**CAGR (Compound Annual Growth Rate):**

```
g = (Ending Value / Beginning Value)^(1/n) - 1
```

Or more explicitly:

```
g = (D_latest / D_earliest)^(1/years) - 1
```

Where:
- **D_latest** = Most recent annual dividend
- **D_earliest** = Dividend from n years ago
- **years** = Number of years between measurements

---

### Step-by-Step Process

#### Step 1: Aggregate Dividends by Year

Companies often pay dividends **multiple times per year** (quarterly, semi-annually).
We first sum all dividends for each calendar year.

**HINDUNILVR Dividend History (Raw Data):**
```
Date          | Dividend
--------------|----------
2020-03-18    | ₹8.00
2020-06-24    | ₹9.50
2020-09-23    | ₹10.00
2020-12-21    | ₹10.00
... (58 total payments from 1998-2025)
```

**After Aggregation (Annual Totals):**
```python
dividends['Year'] = dividends['Date'].dt.year
annual_divs = dividends.groupby('Year')['Dividend'].sum()
```

**Result:**
```
Year  | Total Annual Dividend
------|---------------------
2020  | ₹37.50
2021  | ₹32.00
2022  | ₹36.00
2023  | ₹40.00
2024  | ₹53.00
2025  | ₹24.00 (incomplete year)
```

#### Step 2: Select Time Period

We use the **most recent 5 years** (or less if insufficient data):

```python
years_for_cagr = min(5, len(annual_divs))
annual_divs_recent = annual_divs.tail(years_for_cagr)
```

**For HINDUNILVR:**
```
Selected period: 2021-2025 (5 years of data)
First year (2021): ₹32.00
Last year (2025): ₹24.00
Years: 4 (2021 to 2025 = 4 year periods)
```

#### Step 3: Calculate CAGR

**Formula Application:**
```
g = (D_2025 / D_2021)^(1/4) - 1
g = (24.00 / 32.00)^(1/4) - 1
g = (0.75)^0.25 - 1
g = 0.9306 - 1
g = -0.0694
g = -6.94%
```

**Detailed Breakdown:**
```
Step 1: Ratio of ending to beginning
        24.00 / 32.00 = 0.75

Step 2: Take the 4th root (since n=4 years)
        0.75^(1/4) = 0.75^0.25 = 0.9306

Step 3: Subtract 1 to get growth rate
        0.9306 - 1 = -0.0694

Step 4: Convert to percentage
        -0.0694 × 100 = -6.94%
```

#### Step 4: Apply Safety Caps

To prevent unrealistic values, we cap the growth rate:

```python
cagr = max(min(cagr, 0.20), -0.10)
```

**Rules:**
- **Maximum growth**: +20% (prevents overoptimistic assumptions)
- **Minimum growth**: -10% (handles declining dividends)

**For HINDUNILVR:**
```
Raw CAGR: -6.94%
After capping: -6.94% (within bounds, no change)
Final g = -6.94%
```

---

### Why is HINDUNILVR Growth Negative?

**Year-by-Year Analysis:**
```
2021 → 2022: ₹32.00 → ₹36.00 (+12.5%) ✅
2022 → 2023: ₹36.00 → ₹40.00 (+11.1%) ✅
2023 → 2024: ₹40.00 → ₹53.00 (+32.5%) 🚀
2024 → 2025: ₹53.00 → ₹24.00 (-54.7%) ⚠️
```

**The Problem:**
- **2025 data is INCOMPLETE** (only up to June 2025)
- Company has likely paid only **partial dividends** for the year
- This artificially creates a negative growth rate
- Full year 2025 dividends will likely be higher

**This demonstrates a KEY LIMITATION of using historical CAGR!**

---

### Code Implementation

**Location:** `tools/market_tools.py` (Lines 267-294)

```python
def _calculate_dividend_growth_rate(dividends: pd.DataFrame, years: int = 5) -> float:
    """
    Calculate historical dividend growth rate using CAGR.
    
    CAGR = (Ending Value / Beginning Value)^(1/n) - 1
    """
    # Aggregate by year
    dividends['Year'] = dividends['Date'].dt.year
    annual_divs = dividends.groupby('Year')['Dividend'].sum().sort_index()
    
    if len(annual_divs) < 2:
        logger.warning("Insufficient dividend history")
        return 0.05  # Default 5% growth
    
    # Limit to recent years
    annual_divs = annual_divs.tail(min(years, len(annual_divs)))
    
    # CAGR formula
    n_years = len(annual_divs) - 1
    if n_years == 0 or annual_divs.iloc[0] == 0:
        return 0.05
    
    cagr = (annual_divs.iloc[-1] / annual_divs.iloc[0]) ** (1 / n_years) - 1
    
    # Cap growth rate at reasonable bounds
    cagr = max(min(cagr, 0.20), -0.10)  # Between -10% and +20%
    
    return cagr
```

---

### Alternative Growth Rate Methods (Not Implemented)

#### Method 1: Average Year-over-Year Growth
```
g = Average of [(D_t / D_t-1) - 1] for all years
```

**Pros:** Considers all intermediate years
**Cons:** Sensitive to outliers, volatile

#### Method 2: Linear Regression Trend
```
log(Dividend) = a + b × Year
g = e^b - 1
```

**Pros:** Smooths out volatility
**Cons:** Complex, assumes exponential growth

#### Method 3: Last 3-Year Average
```
g = Average of last 3 year-over-year growth rates
```

**Pros:** Recent data weighted
**Cons:** Still volatile

**We chose CAGR because it's:**
- Industry standard
- Simple and transparent
- Used in most finance textbooks
- Easy to explain in reports

---

## SUMMARY TABLE

| Metric | HINDUNILVR Value | Formula Used | Data Points |
|--------|------------------|--------------|-------------|
| **Beta (β)** | 0.4898 | Linear Regression | 1,235 days |
| **Alpha (α)** | ~0.0001 | Y-intercept | 1,235 days |
| **Correlation** | 0.3438 | Pearson correlation | 1,235 days |
| **Growth Rate (g)** | -6.94% | CAGR | 5 years (2021-2025) |
| **Earliest Dividend** | ₹32.00 (2021) | Sum of year's dividends | - |
| **Latest Dividend** | ₹24.00 (2025) | Sum of year's dividends | - |

---

## FORMULAS SUMMARY

### Beta (β):
```
β = Cov(Stock Returns, Market Returns) / Var(Market Returns)

Using linear regression:
Stock_Return = α + β × Market_Return

β = slope from regression
```

### Growth Rate (g):
```
g = (D_latest / D_earliest)^(1/n) - 1

Where:
- D_latest = Most recent annual dividend
- D_earliest = Dividend n years ago
- n = Number of years

With safety caps:
g_final = max(min(g, 0.20), -0.10)
```

---

## KEY INSIGHTS

### Beta Calculation:
✅ **Strengths:**
- Uses large sample (1,235 days)
- Industry-standard methodology
- Robust statistical measure

⚠️ **Considerations:**
- Historical measure (past ≠ future)
- Can change during market regime shifts
- HINDUNILVR β = 0.49 → Defensive stock

### Growth Rate Calculation:
✅ **Strengths:**
- CAGR is standard in finance
- Simple, transparent formula
- Smooths out year-to-year volatility

⚠️ **Limitations:**
- Historical (doesn't predict future)
- Sensitive to incomplete data (2025 issue)
- Assumes constant growth rate
- HINDUNILVR g = -6.94% → Likely misleading due to incomplete 2025 data

---

## TESTING

To see these calculations in action:

```bash
cd /Users/abelathur/MBA_BITS/Sem3/FM/Assignment
source venv/bin/activate

# Run the detailed walkthrough
python demonstrate_ddm_hindunilvr.py HINDUNILVR

# Or for another company
python demonstrate_ddm_hindunilvr.py TCS
```

This will show you every step of the calculation with actual numbers!

