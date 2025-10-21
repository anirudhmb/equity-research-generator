# DDM (Dividend Discount Model) Calculation - Detailed Explanation

## Overview

We use the **Gordon Growth Model** (a constant-growth DDM) to calculate the intrinsic fair value of dividend-paying stocks.

---

## Formula

```
Fair Value = D₁ / (r - g)
```

Where:
- **D₁** = Expected dividend for next year = D₀ × (1 + g)
- **D₀** = Most recent actual dividend payment
- **r** = Cost of Equity (discount rate)
- **g** = Dividend growth rate

---

## Step-by-Step Calculation Process

### Step 1: Calculate Cost of Equity (r) using CAPM

**Formula:**
```
r = Rf + β × (Rm - Rf)
```

Where:
- **Rf** = Risk-free rate = **7.25%** (Indian 10-Year G-Sec yield)
- **β** = Stock's Beta (systematic risk)
- **Rm** = Expected market return = **13%** (NIFTY 50 historical average)
- **(Rm - Rf)** = Market Risk Premium = **5.75%**

**Example (TCS with β = 0.8):**
```
r = 7.25% + 0.8 × (13% - 7.25%)
r = 7.25% + 0.8 × 5.75%
r = 7.25% + 4.60%
r = 11.85%
```

### Step 2: Calculate Dividend Growth Rate (g)

We calculate the **historical CAGR (Compound Annual Growth Rate)** of dividends over the past 5 years.

**Formula:**
```
g = (Dividend_latest / Dividend_earliest)^(1/n) - 1
```

Where:
- **n** = Number of years
- Dividends are aggregated annually

**Example (Hypothetical):**
```
Year 2020: ₹50 per share
Year 2024: ₹68.93 per share
n = 4 years

g = (68.93 / 50)^(1/4) - 1
g = (1.3786)^0.25 - 1
g = 1.0837 - 1
g = 8.37%
```

**Safety Caps:**
- Maximum growth: **+20%** (prevents unrealistic assumptions)
- Minimum growth: **-10%** (handles declining dividends)

### Step 3: Validate Model Applicability

**Critical Check:** g must be < r

If **g ≥ r**, the Gordon Growth Model is **not applicable** because:
- The denominator (r - g) becomes zero or negative
- This implies infinite or negative valuation (mathematically invalid)
- Indicates a high-growth company that DDM cannot properly value

**Our Implementation:**
```python
if growth_rate >= cost_of_equity:
    return {
        'applicable': False,
        'reason': 'Growth rate exceeds cost of equity - DDM not applicable'
    }
```

### Step 4: Get Most Recent Dividend (D₀)

We fetch the **latest actual dividend payment** from the dividend history.

**Example:**
```
Latest dividend (D₀) = ₹68.93 per share
```

### Step 5: Calculate Next Year's Expected Dividend (D₁)

```
D₁ = D₀ × (1 + g)
```

**Example:**
```
D₁ = ₹68.93 × (1 + 0.0837)
D₁ = ₹68.93 × 1.0837
D₁ = ₹74.70 per share
```

### Step 6: Calculate Fair Value

```
Fair Value = D₁ / (r - g)
```

**Example:**
```
Fair Value = ₹74.70 / (0.1185 - 0.0837)
Fair Value = ₹74.70 / 0.0348
Fair Value = ₹2,146.55 per share
```

### Step 7: Compare with Current Price

**Valuation Metrics:**
```
Current Price = ₹3,739.94
Fair Value = ₹2,146.55

Upside/Downside = (Fair Value - Current Price) / Current Price
Upside/Downside = (₹2,146.55 - ₹3,739.94) / ₹3,739.94
Upside/Downside = -42.6%
```

### Step 8: Generate Recommendation

Our recommendation logic:

| Upside/Downside | Recommendation |
|----------------|----------------|
| > +20% | **Strong Buy** - Undervalued by >20% |
| +10% to +20% | **Buy** - Undervalued by >10% |
| 0% to +10% | **Hold** - Slightly undervalued |
| 0% to -10% | **Hold** - Fairly valued |
| -10% to -20% | **Sell** - Overvalued by >10% |
| < -20% | **Strong Sell** - Overvalued by >20% |

**Example Result:**
```
Recommendation: Strong Sell - Overvalued by >20%
```

---

## Complete Real Example Output

```json
{
    "applicable": true,
    "fair_value": 2146.55,
    "d0_current_dividend": 68.93,
    "d1_next_dividend": 74.70,
    "growth_rate": 0.0837,
    "cost_of_equity": 0.1185,
    "current_price": 3739.94,
    "upside_downside": -0.426,
    "recommendation": "Strong Sell - Overvalued by >20%",
    "formula": "₹74.70 / (11.85% - 8.37%) = ₹2,146.55"
}
```

---

## Key Assumptions & Limitations

### Assumptions:
1. **Constant Growth:** Dividends grow at a constant rate forever
2. **Stable Dividend Policy:** Company maintains consistent dividend payments
3. **Historical Growth:** Past dividend growth predicts future growth
4. **CAPM Validity:** Beta accurately represents systematic risk

### Limitations:
1. **Not Suitable for:**
   - Non-dividend paying stocks (no D₀)
   - High-growth companies (g ≥ r)
   - Companies with erratic dividend policies
   
2. **Historical Bias:**
   - Growth rate (g) is based on **past 5 years**
   - May not reflect future business changes
   - Economic cycles can skew historical averages

3. **Conservative for Growth Stocks:**
   - High-growth companies often show as "overvalued"
   - Example: Tech companies reinvesting profits instead of paying dividends

4. **Sensitivity:**
   - Small changes in g or r can dramatically change fair value
   - A 1% change in (r - g) can change valuation by 20-30%

---

## Why We Use Historical Growth

### Your Question Earlier:
> "Should DDM not be based on future values? We are calculating dividends from past 5 years."

### Our Answer:

**Yes, theoretically DDM should use *future* expected growth**, but:

1. **Assignment Requirements:**
   - Explicitly asks for "5 years of annual financial data"
   - No access to management forecasts or analyst projections
   - Must use publicly available free data sources

2. **Practical Reality:**
   - Future dividend growth is unknowable
   - Analyst forecasts cost money (Bloomberg, FactSet)
   - Historical CAGR is the most objective proxy

3. **Industry Standard:**
   - Most textbook implementations use historical growth
   - Professional analysts adjust based on qualitative factors
   - We add a **disclaimer** in the report acknowledging this limitation

4. **Safety Mechanism:**
   - We cap growth at **20%** to prevent unrealistic valuations
   - We mark DDM as "not applicable" if g ≥ r

---

## Code Implementation

### Location:
```
tools/market_tools.py
```

### Key Functions:

1. **`dividend_discount_model()`** (Lines 167-264)
   - Main DDM calculation
   - Validates applicability
   - Generates recommendation

2. **`_calculate_dividend_growth_rate()`** (Lines 267-294)
   - Calculates historical CAGR
   - Aggregates dividends annually
   - Applies safety caps

3. **`calculate_capm_cost_of_equity()`** (Lines 117-164)
   - Calculates discount rate (r)
   - Uses CAPM formula

4. **`_get_valuation_recommendation()`** (Lines 297-311)
   - Generates buy/hold/sell recommendation
   - Based on upside/downside percentage

---

## Where It Appears in Reports

### Excel Workbook:
- **Sheet: "Valuation"**
  - Fair Value
  - Current Price
  - Upside/Downside
  - Recommendation
  - Formula breakdown

### Word Report:
- **Section: "Valuation Analysis"**
  - LLM synthesizes DDM results
  - Explains recommendation
  - Discusses assumptions

---

## Testing

Run this to see DDM calculation in detail:
```bash
cd /Users/abelathur/MBA_BITS/Sem3/FM/Assignment
source venv/bin/activate
python -c "
from tools.data_tools import fetch_dividends, fetch_company_info
from tools.market_tools import dividend_discount_model, calculate_capm_cost_of_equity

# Fetch data
divs = fetch_dividends('TCS')
info = fetch_company_info('TCS')

# Calculate cost of equity (example beta)
capm = calculate_capm_cost_of_equity(beta=0.8)

# Run DDM
ddm = dividend_discount_model(
    divs, 
    capm['cost_of_equity'],
    current_price=info['current_price']
)

# Print results
print(f\"Fair Value: ₹{ddm['fair_value']:.2f}\")
print(f\"Current Price: ₹{ddm['current_price']:.2f}\")
print(f\"Recommendation: {ddm['recommendation']}\")
"
```

---

## Summary

Our DDM implementation:
- ✅ Uses **Gordon Growth Model** (industry standard)
- ✅ Calculates **r** from CAPM with Indian market parameters
- ✅ Calculates **g** from historical dividend CAGR (5 years)
- ✅ Validates applicability (g < r)
- ✅ Provides clear recommendations
- ⚠️ **Limitation:** Uses historical growth (not forward-looking forecasts)
- ✅ **Mitigation:** Caps growth at 20%, adds disclaimer in reports

This approach is **appropriate for your assignment** given:
- Free data constraints
- Explicit 5-year historical data requirement
- Educational/academic context (not professional investment advice)

