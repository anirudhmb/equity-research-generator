# System Architecture

## Overview

**Automated Equity Research Report Generator** using a **3-Agent Multi-Agent System** orchestrated by LangGraph.

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Streamlit/Gradio Web UI)                    │
│                                                                 │
│  Input: Company Ticker  →  Output: Word Doc + Excel File       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH ORCHESTRATOR                       │
│                    (State Management & Flow)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        ↓                                           ↓
┌──────────────────┐                    ┌──────────────────────┐
│  AGENT 1         │                    │  AGENT 2 & 3         │
│  Data Collection │                    │  (Run in Parallel)   │
└──────────────────┘                    └──────────────────────┘
        ↓                                    ↓           ↓
    CSV Files                         ┌─────────┐  ┌─────────┐
        │                             │ Agent 2 │  │ Agent 3 │
        │                             │ Analyst │  │Research │
        └─────────────────────────────┴─────────┴──┴─────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT GENERATION                          │
│              Word Report + Excel Workbook                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Architecture

### Agent 1: Data Collection & Preparation Agent 📊

**Role:** Acquire and prepare all raw data needed for analysis

**Input:**
- Company ticker symbol
- Configuration (date ranges, data sources)

**Responsibilities:**
1. Fetch 5 years of financial statements
2. Fetch historical stock prices
3. Fetch company metadata and information
4. Fetch competitor data
5. Fetch news and recent developments
6. Clean and validate data
7. Store in structured CSV format

**Tools/Functions:**
```python
- fetch_financial_statements(ticker, years=5)
  ↳ Returns: Income Statement, Balance Sheet, Cash Flow
  
- fetch_stock_prices(ticker, start_date, end_date, frequency='daily')
  ↳ Returns: OHLC price data
  
- fetch_company_info(ticker)
  ↳ Returns: Name, sector, industry, description, employees, etc.
  
- fetch_dividend_history(ticker, years=5)
  ↳ Returns: Dividend payments and dates
  
- fetch_competitors(ticker)
  ↳ Returns: List of competitors with market cap
  
- fetch_news_developments(ticker, months=12)
  ↳ Returns: Recent news articles and events
  
- validate_data(data_dict)
  ↳ Checks completeness and quality
  
- save_to_csv(data, filepath)
  ↳ Saves cleaned data to CSV
```

**Output Structure:**
```
data/{ticker}/
├── financials_income_statement.csv
├── financials_balance_sheet.csv
├── financials_cash_flow.csv
├── stock_prices_daily.csv
├── stock_prices_monthly.csv
├── company_info.json
├── dividend_history.csv
├── competitors.csv
├── news_developments.json
└── data_quality_report.json
```

**Error Handling:**
- Retry failed API calls (max 3 attempts)
- Log missing data points
- Use alternative data sources if primary fails
- Generate data quality report

---

### Agent 2: Financial Analyst Agent 📈

**Role:** Perform all quantitative analysis and calculations

**Input:**
- CSV files from Agent 1
- Analysis configuration

**Responsibilities:**
1. Calculate all financial ratios (liquidity, efficiency, solvency, profitability)
2. Calculate beta using CAPM methodology
3. Perform Dividend Discount Model (DDM) valuation
4. Generate charts and visualizations
5. Create Excel workbook with all calculations
6. Provide numerical insights

**Tools/Functions:**
```python
# Ratio Calculations
- calculate_liquidity_ratios(balance_sheet_df)
  ↳ Current Ratio, Quick Ratio, Cash Ratio
  
- calculate_efficiency_ratios(income_df, balance_df)
  ↳ Asset Turnover, Inventory Turnover, Receivables Turnover
  
- calculate_solvency_ratios(balance_sheet_df, income_df)
  ↳ Debt-to-Equity, Interest Coverage, Debt Ratio
  
- calculate_profitability_ratios(income_df, balance_df)
  ↳ Net Profit Margin, ROE, ROA, Gross Margin

# Risk Analysis
- calculate_returns(price_df)
  ↳ Daily/Monthly returns for stock and market
  
- calculate_beta(stock_returns, market_returns)
  ↳ Beta coefficient using regression
  
- calculate_capm(risk_free_rate, beta, market_return)
  ↳ Expected return / Cost of equity

# Valuation
- perform_ddm_valuation(dividend_df, cost_of_equity, growth_rate)
  ↳ Intrinsic value using Dividend Discount Model
  
- estimate_growth_rate(dividend_df)
  ↳ Historical dividend growth rate

# Visualization
- create_ratio_trend_charts(ratios_df)
  ↳ Line charts for 5-year trends
  
- create_beta_scatter_plot(stock_returns, market_returns)
  ↳ Scatter plot with regression line
  
- create_peer_comparison_chart(company_ratios, competitor_ratios)
  ↳ Bar charts comparing key metrics

# Excel Generation
- create_excel_workbook(all_data)
  ↳ Multi-sheet Excel with data, calculations, charts
```

**Output:**
```
outputs/{ticker}/
├── analysis_results.json          # All calculated metrics
├── ratio_analysis.json             # Detailed ratio breakdown
├── beta_capm_analysis.json         # Risk metrics
├── valuation_analysis.json         # DDM results
├── charts/
│   ├── ratio_trends.png
│   ├── beta_scatter.png
│   ├── dividend_growth.png
│   └── peer_comparison.png
└── {CompanyName}_Financial_Analysis.xlsx
```

**Key Calculations:**
```python
# Example: Beta Calculation
1. Calculate monthly returns: R_t = (P_t - P_{t-1}) / P_{t-1}
2. Get market returns (S&P 500 / NIFTY)
3. Run linear regression: R_stock = α + β × R_market + ε
4. Extract β coefficient
5. Validate: β ≈ 1 (market risk), β > 1 (higher risk), β < 1 (lower risk)
```

---

### Agent 3: Research & Synthesis Agent 📝

**Role:** Conduct qualitative research and generate written report

**Input:**
- CSV files from Agent 1
- Analysis results from Agent 2
- Report template

**Responsibilities:**
1. Research company background and strategy
2. Analyze industry and competitors
3. Synthesize recent developments
4. Generate commentary for all metrics
5. Provide actionable insights
6. Compile final Word document report

**Tools/Functions:**
```python
# Research Tools
- research_company_overview(ticker, company_info)
  ↳ Generate 100-150 word overview using LLM
  
- analyze_corporate_strategy(company_info, financial_data)
  ↳ Assess integration, partnerships, competitive position
  
- analyze_industry_competitors(ticker, competitors_list)
  ↳ Industry structure, market share, competitive landscape
  
- research_recent_developments(news_data)
  ↳ Summarize and assess recent events
  
- web_search(query)
  ↳ Search for additional information

# Synthesis Tools
- generate_ratio_commentary(ratio_name, values, trend)
  ↳ "What's happening? Why? Good or bad?"
  
- generate_performance_insights(all_metrics)
  ↳ Overall assessment and recommendations
  
- generate_management_recommendations(analysis)
  ↳ Actionable insights for decision-makers

# Document Generation
- compile_word_report(template_path, all_data)
  ↳ Fill template with generated content
  
- format_sections(content_dict)
  ↳ Apply proper formatting (headings, bullets, tables)
  
- insert_charts(doc, chart_paths)
  ↳ Embed visualizations in document
```

**Output:**
```
outputs/{ticker}/
├── research_insights.json          # Qualitative findings
├── company_overview.txt            # Written overview
├── strategy_analysis.txt           # Strategy assessment
├── competitor_analysis.txt         # Industry analysis
├── recent_developments.txt         # News synthesis
├── commentary.json                 # Per-metric commentary
└── {CompanyName}_Equity_Research_Report.docx
```

**Content Generation Strategy:**
- Use LLM for creative synthesis
- Ground outputs in factual data
- Apply financial analysis best practices
- Write in professional business tone
- Cite data sources

---

## LangGraph Orchestration

### State Schema

```python
from typing import TypedDict, List, Dict, Optional

class ResearchState(TypedDict):
    # Input
    ticker: str
    company_name: Optional[str]
    
    # Agent 1 Outputs
    data_collected: bool
    csv_paths: Dict[str, str]
    data_quality_score: float
    
    # Agent 2 Outputs
    ratios_calculated: bool
    beta_calculated: bool
    valuation_completed: bool
    analysis_results: Dict
    excel_path: Optional[str]
    
    # Agent 3 Outputs
    research_completed: bool
    report_sections: Dict[str, str]
    word_doc_path: Optional[str]
    
    # Metadata
    errors: List[str]
    warnings: List[str]
    status: str  # 'in_progress', 'completed', 'failed'
```

### Workflow Graph

```python
from langgraph.graph import StateGraph, END

# Define nodes
graph = StateGraph(ResearchState)

# Add nodes
graph.add_node("validate_input", validate_ticker)
graph.add_node("data_collection", agent_1_collect_data)
graph.add_node("validate_data", check_data_quality)
graph.add_node("parallel_analysis", run_agents_2_and_3)
graph.add_node("financial_analysis", agent_2_analyze)
graph.add_node("research_synthesis", agent_3_research)
graph.add_node("compile_reports", generate_documents)
graph.add_node("validate_outputs", check_completeness)

# Define edges
graph.add_edge("validate_input", "data_collection")
graph.add_edge("data_collection", "validate_data")

# Conditional: if data quality good, proceed
graph.add_conditional_edges(
    "validate_data",
    should_continue_after_data_collection,
    {
        "continue": "parallel_analysis",
        "retry": "data_collection",
        "fail": END
    }
)

# Parallel execution
graph.add_edge("parallel_analysis", "financial_analysis")
graph.add_edge("parallel_analysis", "research_synthesis")

# Join after parallel execution
graph.add_edge("financial_analysis", "compile_reports")
graph.add_edge("research_synthesis", "compile_reports")

graph.add_edge("compile_reports", "validate_outputs")
graph.add_edge("validate_outputs", END)

# Set entry point
graph.set_entry_point("validate_input")

# Compile
app = graph.compile()
```

### Execution Flow

```
1. User enters ticker → validate_input
   ├─ Check ticker format
   ├─ Verify ticker exists
   └─ Initialize state

2. data_collection (Agent 1)
   ├─ Fetch financial data (5 years)
   ├─ Fetch stock prices
   ├─ Fetch company info
   ├─ Fetch competitors
   ├─ Fetch news
   └─ Save CSVs

3. validate_data
   ├─ Check completeness
   ├─ Verify data quality
   └─ Decision: continue/retry/fail

4. parallel_analysis (Fork)
   ├─ Branch A: financial_analysis (Agent 2)
   │   ├─ Calculate ratios
   │   ├─ Calculate beta/CAPM
   │   ├─ Perform DDM
   │   ├─ Generate charts
   │   └─ Create Excel
   │
   └─ Branch B: research_synthesis (Agent 3)
       ├─ Research company
       ├─ Analyze strategy
       ├─ Assess competitors
       ├─ Review developments
       └─ Generate commentary

5. compile_reports (Join)
   ├─ Combine Agent 2 + Agent 3 outputs
   ├─ Fill Word template
   ├─ Embed charts
   └─ Final formatting

6. validate_outputs
   ├─ Check all sections present
   ├─ Verify file generation
   └─ Return download links
```

---

## Technology Stack

### Core Framework
- **LangChain**: Agent framework and tool calling
- **LangGraph**: State management and workflow orchestration
- **Python 3.10+**: Primary language

### LLM (Free Options)
**Primary Recommendation: Ollama (Local)**
- **Llama 3** (8B or 70B) - Best for analysis and synthesis
- **Mistral** - Good for structured tasks
- **Gemma** (7B) - Lightweight alternative

**Cloud Alternatives (Free Tiers):**
- **Groq API**: Fast inference, generous free tier
- **Google Gemini**: Free tier (15 requests/min)
- **HuggingFace Inference API**: Various open models

**Advantages of Ollama:**
- ✅ Completely free, no API costs
- ✅ No rate limits
- ✅ Privacy (runs locally)
- ✅ Works offline
- ❌ Requires ~8GB RAM minimum

### Data Sources (All Free - Indian Markets)
- **yfinance**: Yahoo Finance data for NSE/BSE stocks (Free, no API key)
- **NSE India**: Official NSE website scraping for company details
- **MoneyControl**: Company information and news
- **Economic Times**: News and analysis
- **Google News RSS**: Company-specific news feeds
- **BeautifulSoup4**: Web scraping library

### Data Processing
- **pandas**: Data manipulation
- **numpy**: Numerical calculations
- **scipy**: Statistical analysis (regression for beta)

### Visualization
- **matplotlib**: Chart generation
- **seaborn**: Enhanced visualizations
- **plotly**: Interactive charts (optional)

### Document Generation
- **python-docx**: Word document creation
- **openpyxl**: Excel workbook creation
- **Jinja2**: Template rendering

### UI
- **Streamlit**: Web interface
- Alternative: Gradio

### Storage
- **Local filesystem**: CSV and output files
- **SQLite**: Optional metadata storage

---

## Configuration Management

### config/settings.py
```python
# LLM Configuration (Free Options)
LLM_PROVIDER = "ollama"  # Options: "ollama", "groq", "gemini", "huggingface"
OLLAMA_MODEL = "llama3"  # or "mistral", "gemma"
OLLAMA_BASE_URL = "http://localhost:11434"

# Alternative: Groq (if using cloud)
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Free tier available
# GROQ_MODEL = "llama-3-70b"

# Alternative: Google Gemini (if using cloud)  
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Free tier available
# GEMINI_MODEL = "gemini-pro"

# Indian Market Configuration
DEFAULT_MARKET_INDEX = "^NSEI"  # NIFTY 50
RISK_FREE_RATE = 0.0725  # 7.25% - Indian 10-Year G-Sec
EXPECTED_MARKET_RETURN = 0.13  # 13% - Historical NIFTY 50 average

# Market Suffixes
NSE_SUFFIX = ".NS"  # National Stock Exchange
BSE_SUFFIX = ".BO"  # Bombay Stock Exchange

# Timeframes
YEARS_OF_DATA = 5
MONTHS_OF_NEWS = 12

# Retry Logic
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Output
OUTPUT_DIR = "outputs"
DATA_DIR = "data"

# News Sources (Free)
NEWS_SOURCES = [
    "https://www.moneycontrol.com",
    "https://economictimes.indiatimes.com",
    "https://www.nseindia.com"
]
```

---

## Security & Best Practices

### API Key Management
- Store in `.env` file (never commit)
- Use environment variables
- Rotate keys regularly

### Data Privacy
- No PII collection
- Public data only
- Respect robots.txt

### Error Handling
- Graceful degradation
- Detailed logging
- User-friendly error messages

### Testing
- Unit tests for each tool
- Integration tests for agents
- End-to-end tests for full workflow

### Monitoring
- Log all agent activities
- Track API usage
- Monitor generation times

---

## Scalability Considerations

### Current Design (MVP)
- Sequential processing: 1 company at a time
- ~5 minutes per company
- Local file storage

### Future Enhancements
- Queue system for multiple companies
- Distributed processing
- Cloud storage (S3/GCS)
- Caching of common data
- Database for historical reports

---

## Development Workflow

```
1. Development
   └─ Local environment with test data

2. Testing
   ├─ Unit tests (pytest)
   ├─ Integration tests
   └─ Manual validation

3. Deployment
   └─ Streamlit Cloud / Docker container

4. Monitoring
   └─ Logs and error tracking
```

---

## File Structure

```
Assignment/
├── agents/
│   ├── __init__.py
│   ├── data_agent.py          # Agent 1
│   ├── analyst_agent.py       # Agent 2
│   └── research_agent.py      # Agent 3
│
├── tools/
│   ├── __init__.py
│   ├── data_tools.py          # Financial API tools
│   ├── analysis_tools.py      # Calculation functions
│   ├── research_tools.py      # Web search, synthesis
│   └── document_tools.py      # Word/Excel generation
│
├── orchestrator/
│   ├── __init__.py
│   ├── graph.py               # LangGraph workflow
│   └── state.py               # State schema
│
├── ui/
│   └── app.py                 # Streamlit UI
│
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration
│
├── utils/
│   ├── __init__.py
│   ├── validators.py          # Input validation
│   └── helpers.py             # Utility functions
│
├── tests/
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_integration.py
│
├── data/                      # Generated CSV storage
├── outputs/                   # Generated reports
├── templates/                 # Original DOCX template
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
│
├── .env                       # API keys (gitignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Success Metrics

### Performance
- ✅ Report generation < 5 minutes
- ✅ 95%+ data collection success rate
- ✅ <1% calculation errors

### Quality
- ✅ Reports match manual research quality
- ✅ All mandatory sections complete
- ✅ Professional presentation

### Reliability
- ✅ Handles 90%+ of S&P 500 / NIFTY 50 companies
- ✅ Graceful handling of missing data
- ✅ Clear error messages

