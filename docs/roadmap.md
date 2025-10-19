# Implementation Roadmap

## Project Timeline: Automated Equity Research Report Generator

**Estimated Total Time:** 15-20 hours of development  
**Target Completion:** Before October 31, 2025  
**Last Updated:** October 19, 2025

---

## 📊 Progress Overview

| Phase | Status | Completion | Notes |
|-------|--------|------------|-------|
| **Phase 1: Setup & Environment** | ✅ Complete | 100% (3/3) | Environment ✅, Config ✅, Testing ✅ |
| **Phase 2: Data Collection Tools** | 🔄 In Progress | 50% (2/4) | Data Tools ✅, Ratios ✅ |
| **Phase 3: Agent Development** | ⏳ Pending | 0% | - |
| **Phase 4: LangGraph Orchestration** | ⏳ Pending | 0% | - |
| **Phase 5: Report Generation** | ⏳ Pending | 0% | - |
| **Phase 6: UI Development** | ⏳ Pending | 0% | - |
| **Phase 7: Testing & Refinement** | ⏳ Pending | 0% | - |

**Current Focus:** Phase 2 Step 2.3 - Building market data tools (Beta, CAPM, DDM)

---

## Phase 1: Project Setup & Environment (1-2 hours)

### ✅ Step 1.1: Environment Setup
**Duration:** 30 minutes  
**Status:** ✅ COMPLETED on Oct 19, 2025

- [x] Create organized directory structure
- [x] Set up Python virtual environment (`venv/`)
- [x] Install core dependencies (all packages from requirements.txt)
- [x] Create requirements.txt (54 packages including langchain, yfinance, groq, etc.)
- [x] Set up .env file for API keys (template created, user needs to add Groq key)
- [x] Initialize git repository (connected to GitHub: anirudhmb/equity-research-generator)

**Notes:**
- Using **Groq** as LLM provider (free tier, llama-3.1-70b-versatile)
- Virtual environment activated at: `/Users/abelathur/MBA_BITS/Sem3/FM/Assignment/venv`
- All dependencies installed successfully
- Git configured with cross-platform support (.gitattributes, .gitignore)

**Deliverables:**
```bash
# Install Ollama first (for free local LLM)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3  # or mistral/gemma

# Python dependencies
pip install langchain langgraph langchain-ollama
pip install yfinance pandas numpy scipy
pip install matplotlib seaborn
pip install python-docx openpyxl
pip install streamlit python-dotenv beautifulsoup4 requests
pip install feedparser  # For news RSS feeds
```

---

### ✅ Step 1.2: Configuration Setup
**Duration:** 30 minutes  
**Status:** ✅ COMPLETED on Oct 19, 2025

- [x] Create config/settings.py (290+ lines with full configuration management)
- [x] Set up LLM configuration (Groq/Ollama/Gemini support)
- [x] Define Indian market constants:
  - NIFTY 50 as benchmark (^NSEI) ✅
  - Indian G-Sec rate (~7.25%) ✅
  - NSE/BSE ticker suffixes (.NS, .BO) ✅
  - Market Risk Premium calculation ✅
- [x] Create logging configuration (utils/logger.py with colored console + file logging)
- [x] Set up error handling framework (validation functions, retry logic)

**Deliverables:**
- ✅ `config/settings.py` with all configurations
- ✅ `config/__init__.py` for package initialization
- ✅ `config/env_template.txt` for optional API keys
- ✅ `utils/logger.py` with loguru integration
- ✅ `.env.example` template (Git-safe)

**Notes:**
- Configuration validates API keys, financial parameters, and file paths
- Supports multiple LLM providers with easy switching
- Indian market constants: Risk-Free=7.25%, Expected Return=13%, Premium=5.75%
- Logger outputs to both console (colored) and file (logs/ directory)

---

### ✅ Step 1.3: Test Data Acquisition
**Duration:** 30 minutes  
**Status:** ✅ COMPLETED on Oct 19, 2025

- [x] Test yfinance API with sample ticker (tested NIFTY 50 + 5 companies)
- [x] Verify data availability for 1-2 companies (tested 5 across sectors)
- [x] Document data format and structure (comprehensive test output)
- [x] Identify any data gaps (none - all data available!)

**Test Results:** 6/6 tests passed (100%)
- ✅ NIFTY 50: 1,236 days, 18.22% annual return
- ✅ RELIANCE (Energy): Full data, ₹19.17T market cap
- ✅ TCS (IT): Full data, ₹10.72T market cap
- ✅ INFY (IT): Full data, ₹5.97T market cap
- ✅ HDFCBANK (Banking): Full data, ₹15.40T market cap
- ✅ ITC (FMCG): Full data, ₹5.16T market cap

**Data Confirmed Available:**
- Company info (name, sector, industry, market cap, PE ratio)
- 5 years of historical stock prices
- Financial statements (Income, Balance Sheet, Cash Flow) - 5 periods
- Dividend history
- Quarterly financials - 6 quarters

**Test Commands:**
```python
import yfinance as yf

# Test with Indian company (NSE)
ticker = yf.Ticker("RELIANCE.NS")
print(ticker.info)
print(ticker.financials)
print(ticker.history(period="5y"))

# Test with NIFTY 50 index
nifty = yf.Ticker("^NSEI")
print(nifty.history(period="5y"))
```

---

## Phase 2: Data Collection Tools (3-4 hours)

### ✅ Step 2.1: Financial Data Tools
**Duration:** 1.5 hours  
**Status:** ✅ COMPLETED on Oct 19, 2025

**Files Created:**
- ✅ `tools/__init__.py`
- ✅ `tools/data_tools.py` (600+ lines, 15 functions)

**Functions Implemented:**
```python
✅ 1. fetch_company_info(ticker, exchange) - Comprehensive company data
✅ 2. fetch_stock_prices(ticker, exchange, years) - Historical OHLCV + returns
✅ 3. fetch_financial_statements(ticker, quarterly) - Income, Balance, Cash Flow
✅ 4. calculate_returns_metrics(prices) - Returns, volatility, Sharpe
✅ 5. fetch_dividends(ticker) - Dividend history
✅ 6. calculate_dividend_metrics(dividends, price) - Yield, growth rate
✅ 7. fetch_market_index_data(index) - NIFTY 50 benchmark data
✅ 8. get_aligned_returns(stock, market) - For beta calculation
✅ 9. save_data_to_csv(data, ticker, type) - Data persistence
✅ 10. fetch_all_company_data(ticker) - Complete data fetch
```

**Additional Features:**
- Retry decorator for API failures (MAX_RETRIES with exponential backoff)
- Timezone-aware datetime handling
- Moving averages (MA_50, MA_200)
- Period returns (YTD, MTD, 1Y, 3Y, 5Y)
- Dividend frequency detection
- Comprehensive error handling and logging

**Test Results:**
- ✅ Tested with RELIANCE stock
- ✅ 1,237 price points fetched
- ✅ 10.85% annual return calculated
- ✅ All financial statements retrieved
- ✅ 30 dividend payments processed
- ✅ Data saved to CSV successfully

---

### ✅ Step 2.2: Financial Ratio Calculator
**Duration:** 1 hour  
**Status:** ✅ COMPLETED on Oct 19, 2025

**Files Created:**
- ✅ `tools/ratio_calculator.py` (700+ lines with comprehensive ratio analysis)

**Ratios Implemented (18 total):**

**Liquidity Ratios (3):**
```python
✅ 1. current_ratio() - Current Assets / Current Liabilities
✅ 2. quick_ratio() - (Current Assets - Inventory) / Current Liabilities
✅ 3. cash_ratio() - Cash / Current Liabilities
```

**Efficiency Ratios (4):**
```python
✅ 4. asset_turnover() - Revenue / Total Assets
✅ 5. inventory_turnover() - COGS / Inventory
✅ 6. receivables_turnover() - Revenue / Receivables
✅ 7. days_sales_outstanding() - 365 / Receivables Turnover
```

**Solvency/Leverage Ratios (4):**
```python
✅ 8. debt_to_equity() - Total Debt / Total Equity
✅ 9. debt_ratio() - Total Liabilities / Total Assets
✅ 10. interest_coverage() - EBIT / Interest Expense
✅ 11. equity_multiplier() - Total Assets / Total Equity
```

**Profitability Ratios (7):**
```python
✅ 12. gross_profit_margin() - Gross Profit / Revenue
✅ 13. operating_profit_margin() - Operating Income / Revenue
✅ 14. net_profit_margin() - Net Income / Revenue
✅ 15. return_on_assets() - Net Income / Total Assets
✅ 16. return_on_equity() - Net Income / Shareholders' Equity
✅ 17. return_on_invested_capital() - NOPAT / Invested Capital
```

**Additional Features:**
- RatioCalculator class with intelligent field mapping
- Handles yfinance field name variations automatically
- calculate_all_ratios() - Batch calculation for all periods
- calculate_ratio_trends() - Multi-period trend analysis
- get_ratio_summary() - Categorized ratio grouping
- Comprehensive error handling and logging

**Test Results (RELIANCE):**
- ✅ 17/17 ratios calculated successfully (100%)
- ✅ Current Ratio: 1.10 (Good liquidity)
- ✅ Gross Margin: 25.09% (Strong)
- ✅ Net Margin: 7.22% (Solid)
- ✅ ROE: 8.26% (Decent)
- ✅ Debt-to-Equity: 0.37 (Low leverage)
- ✅ Interest Coverage: 5.79x (Strong)

---

### 🔧 Step 2.3: Market Data Tools (Beta, CAPM, DDM)
**Duration:** 1 hour

**Files to Create:**
- `tools/market_tools.py`

**Functions to Implement:**
```python
1. calculate_beta(stock_returns, market_returns)
   - Beta vs NIFTY 50
   - Regression analysis
   
2. calculate_capm_cost_of_equity(risk_free_rate, beta, market_return)
   - CAPM formula
   - Indian G-Sec rate
   
3. dividend_discount_model(dividends, growth_rate, cost_of_equity)
   - DDM valuation
   - Fair value estimation
   
4. calculate_market_risk_premium()
   - Historical market returns
   - Risk-free rate
```

---

### 🔧 Step 2.4: News & Research Tools
**Duration:** 1.5 hours

**Files to Create:**
- `tools/news_scraper.py`

**Functions to Implement:**
```python
1. fetch_indian_news(ticker, months=12)
   - MoneyControl news scraping
   - Economic Times articles
   - Google News RSS feeds
   
2. fetch_nse_company_info(ticker)
   - Scrape NSE India website
   - Company announcements
   - Corporate actions
   
3. fetch_competitors(ticker)
   - Industry peers from NSE/BSE
   - Market cap comparison
```

---

## Phase 3: Agent 1 - Data Collection Agent (2-3 hours)

### 🤖 Step 3.1: Agent Implementation
**Duration:** 1.5 hours

**Files to Create:**
- `agents/data_agent.py`

**Implementation:**
```python
class DataCollectionAgent:
    def __init__(self, llm, tools):
        """Initialize with LLM and data tools"""
        
    def collect_all_data(self, ticker):
        """Main orchestration method"""
        # 1. Validate ticker
        # 2. Fetch financial statements
        # 3. Fetch stock prices
        # 4. Fetch company info
        # 5. Fetch competitors
        # 6. Fetch news
        # 7. Validate and save
        # 8. Return CSV paths
```

**Agent Behavior:**
- Uses LangChain's agent framework
- Reasons about what data to fetch
- Handles missing data gracefully
- Retries failed API calls

---

### 🤖 Step 3.2: Testing & Validation
**Duration:** 1 hour

- [ ] Test with 3 different companies
- [ ] Verify CSV output format
- [ ] Test error handling (invalid ticker)
- [ ] Test retry logic
- [ ] Generate data quality reports

**Deliverables:**
- Fully functional Data Collection Agent
- Sample CSV files for test companies
- Test suite passing

---

## Phase 4: Analysis Tools (3-4 hours)

### 📊 Step 4.1: Ratio Calculation Tools
**Duration:** 2 hours

**Files to Create:**
- `tools/analysis_tools.py`

**Functions to Implement:**
```python
# Liquidity Ratios
1. calculate_current_ratio(balance_sheet)
2. calculate_cash_ratio(balance_sheet)

# Efficiency Ratios
3. calculate_asset_turnover(income, balance_sheet)
4. calculate_inventory_turnover(income, balance_sheet)
5. calculate_receivables_turnover(income, balance_sheet)

# Solvency Ratios
6. calculate_debt_to_equity(balance_sheet)
7. calculate_interest_coverage(income)

# Profitability Ratios
8. calculate_net_profit_margin(income)
9. calculate_roe(income, balance_sheet)
10. calculate_roa(income, balance_sheet)
11. calculate_gross_margin(income)

# Helper function
12. calculate_all_ratios(financial_data)
    - Returns dictionary with all ratios for 5 years
```

---

### 📊 Step 4.2: Risk Analysis Tools (CAPM/Beta)
**Duration:** 1.5 hours

**Functions to Implement:**
```python
1. calculate_returns(price_data)
   - Convert prices to returns
   
2. calculate_beta(stock_returns, market_returns)
   - Linear regression
   - Return beta coefficient
   
3. calculate_statistics(returns)
   - Mean, std dev, Sharpe ratio
   
4. calculate_capm(risk_free_rate, beta, market_return)
   - Expected return / Cost of equity
```

**Testing:**
- Verify beta matches published values
- Test with known high-beta and low-beta stocks

---

### 📊 Step 4.3: Valuation Tools
**Duration:** 1 hour

**Functions to Implement:**
```python
1. estimate_dividend_growth_rate(dividend_history)
   - Historical growth calculation
   
2. perform_ddm_valuation(dividend, growth_rate, cost_of_equity)
   - Gordon Growth Model
   - Return intrinsic value
   
3. compare_to_market_price(intrinsic_value, market_price)
   - Generate recommendation
```

---

## Phase 5: Agent 2 - Financial Analyst Agent (2-3 hours)

### 🤖 Step 5.1: Agent Implementation
**Duration:** 1.5 hours

**Files to Create:**
- `agents/analyst_agent.py`

**Implementation:**
```python
class FinancialAnalystAgent:
    def __init__(self, llm, analysis_tools):
        """Initialize with LLM and calculation tools"""
        
    def analyze(self, csv_paths):
        """Main analysis orchestration"""
        # 1. Load CSV data
        # 2. Calculate all ratios
        # 3. Calculate beta/CAPM
        # 4. Perform DDM valuation
        # 5. Generate insights
        # 6. Return structured results
```

---

### 🤖 Step 5.2: Visualization Tools
**Duration:** 1 hour

**Files to Create:**
- `tools/visualization_tools.py`

**Functions to Implement:**
```python
1. create_ratio_trend_chart(ratio_data, ratio_name)
2. create_beta_scatter_plot(stock_returns, market_returns)
3. create_dividend_growth_chart(dividend_history)
4. create_peer_comparison_chart(company_data, peer_data)
```

---

### 🤖 Step 5.3: Excel Generation
**Duration:** 1 hour

**Files to Create:**
- `tools/excel_tools.py`

**Implementation:**
```python
def create_excel_workbook(ticker, all_data):
    # Sheet 1: Raw Financial Data
    # Sheet 2: Ratio Calculations
    # Sheet 3: Beta/CAPM Analysis
    # Sheet 4: DDM Valuation
    # Sheet 5: Charts
    # Sheet 6: Summary
```

**Deliverables:**
- Fully functional Analyst Agent
- Sample Excel workbooks
- All charts generated

---

## Phase 6: Agent 3 - Research & Synthesis Agent (2-3 hours)

### 🤖 Step 6.1: Research Tools
**Duration:** 1 hour

**Files to Create:**
- `tools/synthesis_tools.py`

**Functions to Implement:**
```python
1. generate_company_overview(company_info, llm)
2. analyze_corporate_strategy(company_info, financials, llm)
3. analyze_competitors(company_data, competitor_data, llm)
4. synthesize_recent_developments(news_data, llm)
5. generate_ratio_commentary(ratio_name, values, trend, llm)
```

---

### 🤖 Step 6.2: Agent Implementation
**Duration:** 1.5 hours

**Files to Create:**
- `agents/research_agent.py`

**Implementation:**
```python
class ResearchSynthesisAgent:
    def __init__(self, llm, research_tools):
        """Initialize with LLM and synthesis tools"""
        
    def research_and_write(self, csv_paths, analysis_results):
        """Main research orchestration"""
        # 1. Generate company overview
        # 2. Analyze strategy
        # 3. Research competitors
        # 4. Synthesize developments
        # 5. Create commentary for all metrics
        # 6. Return structured content
```

---

### 🤖 Step 6.3: Document Generation
**Duration:** 1 hour

**Files to Create:**
- `tools/document_tools.py`

**Functions to Implement:**
```python
1. load_template(template_path)
2. fill_template_section(doc, section_name, content)
3. insert_table(doc, data)
4. insert_chart(doc, image_path)
5. apply_formatting(doc)
6. save_document(doc, output_path)
```

**Deliverables:**
- Fully functional Research Agent
- Sample Word documents

---

## Phase 7: LangGraph Orchestration (2-3 hours)

### 🔄 Step 7.1: State Management
**Duration:** 1 hour

**Files to Create:**
- `orchestrator/state.py`

**Implementation:**
```python
class ResearchState(TypedDict):
    ticker: str
    company_name: Optional[str]
    data_collected: bool
    csv_paths: Dict[str, str]
    analysis_results: Dict
    research_results: Dict
    excel_path: Optional[str]
    word_doc_path: Optional[str]
    errors: List[str]
    status: str
```

---

### 🔄 Step 7.2: Graph Construction
**Duration:** 1.5 hours

**Files to Create:**
- `orchestrator/graph.py`

**Implementation:**
```python
1. Define all nodes (agents and validators)
2. Define edges (workflow transitions)
3. Add conditional edges (error handling)
4. Set up parallel execution for Agent 2 & 3
5. Compile graph
```

---

### 🔄 Step 7.3: Integration Testing
**Duration:** 1 hour

- [ ] Test end-to-end flow with 1 company
- [ ] Test error scenarios
- [ ] Test partial data scenarios
- [ ] Verify all outputs generated correctly

**Deliverables:**
- Working orchestrator
- Complete reports for test companies

---

## Phase 8: User Interface (2-3 hours)

### 🖥️ Step 8.1: Streamlit UI
**Duration:** 2 hours

**Files to Create:**
- `ui/app.py`

**Features:**
```python
1. Ticker input field
2. "Generate Report" button
3. Progress indicator
   - Data collection progress
   - Analysis progress
   - Report generation progress
4. Error display (if any)
5. Download buttons for Word + Excel
6. Preview of key metrics
7. View generated charts
```

---

### 🖥️ Step 8.2: UI Testing & Polish
**Duration:** 1 hour

- [ ] Test with multiple companies
- [ ] Improve error messages
- [ ] Add loading animations
- [ ] Style improvements
- [ ] Mobile responsiveness

**Deliverables:**
- Polished, user-friendly UI
- Deployed locally or on Streamlit Cloud

---

## Phase 9: Testing & Quality Assurance (2-3 hours)

### ✅ Step 9.1: Comprehensive Testing
**Duration:** 2 hours

**Test Cases:**
1. **Happy Path:** Popular companies (AAPL, MSFT, GOOGL)
2. **Edge Cases:**
   - Recently IPO'd companies
   - Non-dividend paying stocks
   - Companies with missing data
   - International tickers
3. **Error Cases:**
   - Invalid ticker
   - Delisted companies
   - Network errors

**Testing Checklist:**
- [ ] All calculations match manual verification
- [ ] All report sections present
- [ ] Charts display correctly
- [ ] Excel formulas work
- [ ] Word document formatting correct

---

### ✅ Step 9.2: Validation Against Assignment
**Duration:** 1 hour

**Verify:**
- [ ] ✅ Company not a bank/financial institution
- [ ] ✅ 5 years of data included
- [ ] ✅ Minimum 6 ratios calculated
- [ ] ✅ Line charts for trends
- [ ] ✅ Commentary for each metric
- [ ] ✅ Beta and CAPM included
- [ ] ✅ DDM valuation performed
- [ ] ✅ Strategy analysis present
- [ ] ✅ Competitor analysis present
- [ ] ✅ Recent developments included
- [ ] ✅ Both Word + Excel files generated

---

## Phase 10: Documentation & Deployment (1-2 hours)

### 📚 Step 10.1: Documentation
**Duration:** 1 hour

**Files to Create/Update:**
- [ ] README.md with usage instructions
- [ ] API documentation for tools
- [ ] Troubleshooting guide
- [ ] Sample outputs

---

### 🚀 Step 10.2: Deployment
**Duration:** 1 hour

**Options:**
1. **Local:** Instructions for running locally
2. **Streamlit Cloud:** Deploy UI
3. **Docker:** Containerize application (optional)

**Deliverables:**
- Deployed application
- User guide

---

## Milestone Checklist

### Milestone 1: Data Pipeline ✅
- [ ] All data tools implemented
- [ ] Agent 1 fully functional
- [ ] CSV outputs validated

### Milestone 2: Analysis Engine ✅
- [ ] All calculation tools implemented
- [ ] Agent 2 fully functional
- [ ] Excel outputs validated

### Milestone 3: Report Generator ✅
- [ ] All synthesis tools implemented
- [ ] Agent 3 fully functional
- [ ] Word outputs validated

### Milestone 4: System Integration ✅
- [ ] LangGraph orchestrator working
- [ ] End-to-end flow tested
- [ ] Error handling verified

### Milestone 5: User Interface ✅
- [ ] Streamlit UI complete
- [ ] User-friendly and intuitive
- [ ] Download functionality working

### Milestone 6: Production Ready ✅
- [ ] Comprehensive testing complete
- [ ] Documentation complete
- [ ] Deployed and accessible

---

## Risk Mitigation

### Potential Risks & Solutions

**Risk 1: API Rate Limits**
- Solution: Implement caching, use multiple data sources

**Risk 2: LLM Token Limits**
- Solution: Chunk large documents, summarize intermediates

**Risk 3: Missing Financial Data**
- Solution: Graceful degradation, clear warnings

**Risk 4: Calculation Errors**
- Solution: Extensive unit tests, validation against known values

**Risk 5: Time Constraints**
- Solution: Prioritize MVP features, defer nice-to-haves

---

## Development Principles

1. **Incremental Development**: Build and test one component at a time
2. **Test Early**: Write tests alongside code
3. **Iterate**: Start simple, add complexity
4. **Document**: Comment code, update docs
5. **Version Control**: Commit frequently with clear messages

---

## Success Criteria

### MVP (Minimum Viable Product)
✅ Generates complete report for 1 company
✅ All calculations correct
✅ Professional-looking output
✅ Works for 80% of S&P 500 companies

### Full Success
✅ Works for 95%+ of public companies
✅ <5 minute generation time
✅ Beautiful UI
✅ Comprehensive error handling
✅ Ready for real-world use

---

## Next Steps

**Immediate:**
1. Review this roadmap
2. Set up development environment
3. Begin Phase 1

**After MVP:**
1. Gather feedback
2. Iterate on quality
3. Add enhancements

---

## Questions Before Starting?

- ✅ **LLM**: Ollama installed? (Recommended) - OR using Groq/Gemini free tier?
- ✅ **Data Source**: yfinance is perfect for Indian markets (NSE/BSE) - No keys needed!
- ✅ **Deployment**: Local deployment (Streamlit) is best for free setup
- ✅ **Test Companies**: Which Indian companies to test with?
  - Suggested: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS

**Ready to begin? Let's start with Phase 1! 🚀**

**Note**: Everything is 100% free - No paid APIs or subscriptions required!

