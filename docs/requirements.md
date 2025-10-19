# Requirements Document

## Project Overview
**Automated Equity Research Report Generator**

An AI-powered system that automatically generates comprehensive equity research reports for publicly traded companies using a 3-agent architecture with LangChain and LangGraph.

---

## Business Requirements

### Primary Goal
Automate the complete equity research report generation process as per MBA BITS FM Assignment guidelines, eliminating manual data collection and analysis.

### Input
- **Company Ticker/Scrip Code** for Indian companies (e.g., "RELIANCE.NS", "TCS.BO", "INFY.NS")
  - NSE (National Stock Exchange): Use `.NS` suffix
  - BSE (Bombay Stock Exchange): Use `.BO` suffix
- Market: Focus exclusively on Indian stock markets (NSE/BSE)

### Output
1. **Word Document**: Comprehensive equity research report following the prescribed template
2. **Excel Workbook**: Financial data, calculations, and analysis
3. Both files ready for submission

---

## Functional Requirements

### 1. Data Collection & Preparation
**Must Collect:**
- ✅ 5 years of financial statements (Income Statement, Balance Sheet, Cash Flow)
- ✅ Daily/Monthly stock prices for last 5 years (for beta calculation)
- ✅ Company metadata (name, industry, sector, description, leadership)
- ✅ Dividend history (for DDM valuation)
- ✅ Competitor information and market share data
- ✅ Recent news and developments
- ✅ Industry trends and benchmarks

**Data Sources (All Free):**
- Primary: **yfinance** (Free, supports NSE/BSE tickers with .NS and .BO suffixes)
- Secondary: **NSE India website** scraping (for additional company info)
- News: **Google News** RSS feeds, **MoneyControl**, **Economic Times**
- Backup: Manual data upload capability

**Note:** All data sources are free and do not require API keys.

**Output:**
- Clean, validated CSV files stored in `data/{ticker}/` directory
- Data quality report with completeness metrics

---

### 2. Financial Analysis & Calculations

#### 2.1 Ratio Analysis (Minimum 6 Ratios Required)
**Liquidity Ratios:**
- Current Ratio = Current Assets / Current Liabilities
- Cash Ratio = (Cash + Cash Equivalents) / Current Liabilities

**Efficiency Ratios:**
- Asset Turnover Ratio = Revenue / Total Assets
- Inventory Turnover Ratio = COGS / Average Inventory
- Receivables Turnover Ratio = Revenue / Average Accounts Receivable

**Solvency/Leverage Ratios:**
- Debt-to-Equity Ratio = Total Debt / Total Equity
- Interest Coverage Ratio = EBIT / Interest Expense

**Profitability Ratios:**
- Net Profit Margin = Net Income / Revenue
- Return on Equity (ROE) = Net Income / Shareholders' Equity
- Return on Assets (ROA) = Net Income / Total Assets
- Gross Profit Margin = (Revenue - COGS) / Revenue

#### 2.2 Risk Analysis (CAPM)
- Calculate monthly stock returns (5 years)
- Calculate market returns using **NIFTY 50** (^NSEI) as benchmark index
- Calculate Beta (β) = Covariance(Stock, Market) / Variance(Market)
- Calculate standard deviation of returns
- Apply CAPM: Cost of Equity = Risk-Free Rate + Beta × (Market Return - Risk-Free Rate)
  - Use **Indian 10-Year G-Sec yield** (~7-7.5%) as Risk-Free Rate
  - Market Return: Historical average of NIFTY 50 (~12-14%)

#### 2.3 Valuation
**Dividend Discount Model (DDM):**
- Intrinsic Value = D₁ / (r - g)
  - D₁ = Expected dividend next year
  - r = Required rate of return (from CAPM)
  - g = Dividend growth rate
- Compare intrinsic value vs. current market price
- Investment recommendation (Buy/Hold/Sell)

#### 2.4 Visualizations
- Line charts for ratio trends (5 years)
- Beta scatter plot (stock vs market returns)
- Dividend growth chart
- Competitor comparison charts
- Performance vs. benchmark index

---

### 3. Research & Synthesis

#### 3.1 Company Overview (100-150 words)
- Company history and age
- Size (headcount, revenue)
- Geographic operations
- Products and services description
- Unique characteristics/competitive advantages
- Leadership team (CEO, CFO, Board Chair)
- Mission and vision statements

#### 3.2 Corporate Strategy Analysis
- Vertical vs. horizontal integration
- Supplier relationships
- Customer profile
- Strategic partnerships/alliances/joint ventures
- Competitive advantages and disadvantages

#### 3.3 Industry & Competitor Analysis
- Industry structure (fragmented vs. concentrated)
- Major competitors by product/service line
- Market share attribution
- Ranking among competitors
- Opportunities and threats

#### 3.4 Recent Developments
- New products/services launched
- New market entries
- Mergers, acquisitions, divestitures
- Management changes
- Regulatory impacts
- Upcoming events and their expected impact

#### 3.5 Commentary & Insights
For each financial metric:
- **What is happening?** (trend description)
- **Significance?** (why it matters)
- **Performance assessment** (good/poor/neutral)
- **Actionable insights** for senior management

---

## Technical Requirements

### System Architecture
- **Framework**: LangChain + LangGraph for agent orchestration
- **LLM Options** (All Free):
  - **Ollama** (Local): Llama 3, Mistral, Gemma (Recommended - No API costs)
  - **Groq API** (Cloud): Free tier with fast inference
  - **HuggingFace Inference API**: Free tier available
  - **Google Gemini**: Free tier (15 requests/min)
- **Programming Language**: Python 3.10+
- **UI Framework**: Streamlit (Free hosting available)

### Agent Architecture
**3 Specialized Agents:**
1. Data Collection Agent
2. Financial Analyst Agent
3. Research & Synthesis Agent

### Performance Requirements
- Report generation time: < 5 minutes per company
- Data freshness: Use most recent available data
- Error handling: Graceful degradation if partial data unavailable
- Retry logic: 3 attempts for failed API calls

### Data Storage
- CSV files for structured financial data
- JSON files for intermediate agent outputs
- Persistent storage in `data/` and `outputs/` directories

### Document Generation
- Word document: Follow template structure exactly
- Excel workbook: Multiple sheets (Raw Data, Calculations, Charts, Summary)
- File naming: `{CompanyName}_Equity_Research_{Date}.docx/xlsx`

---

## Quality Requirements

### Accuracy
- ✅ All calculations must be mathematically correct
- ✅ Financial ratios must match standard definitions
- ✅ Data must be from reliable sources
- ✅ Citations and data sources clearly mentioned

### Completeness
- ✅ All mandatory sections filled
- ✅ Minimum 6 ratios calculated
- ✅ 5 years of historical data
- ✅ All visualizations generated

### Presentation
- ✅ Professional formatting
- ✅ Clear, concise writing (business English)
- ✅ Proper charts and tables
- ✅ Consistent styling

### Compliance
- ✅ Follows assignment template exactly
- ✅ Includes all required sections
- ✅ Ready for submission without manual editing

---

## Constraints & Limitations

### Must NOT Include
- ❌ Financial institutions or banks (per assignment rules)
- ❌ Companies with insufficient data (< 3 years)
- ❌ Unverified or questionable data sources

### Dependencies
- Internet connection required (API access)
- API keys/credentials needed (OpenAI, Financial APIs)
- Sufficient LLM token limits

### Edge Cases to Handle
- Company recently IPO'd (< 5 years data)
- Company doesn't pay dividends (DDM alternative)
- Missing financial data for specific quarters
- Company name vs ticker ambiguity
- Multiple stock listings (different exchanges)

---

## Success Criteria

### Minimum Viable Product (MVP)
✅ Generates report for 1 company successfully
✅ Contains all mandatory sections
✅ Calculations are accurate
✅ Word + Excel files downloadable

### Full Success
✅ Works for any publicly traded non-financial company
✅ Report quality matches manual research
✅ < 5 minute generation time
✅ Professional presentation quality
✅ Can handle 10+ companies in parallel

### Exceptional
✅ Insights rival professional analysts
✅ Automated peer review and validation
✅ Multi-language support
✅ Real-time data updates
✅ Comparison across multiple companies

---

## Future Enhancements (Out of Scope for MVP)

- PDF generation option
- Email delivery of reports
- Scheduled automatic updates
- Portfolio analysis (multiple companies)
- Custom template support
- Integration with Bloomberg/Prowess
- Natural language query interface
- Comparison report generator
- ESG analysis addition
- Sentiment analysis from news/social media

