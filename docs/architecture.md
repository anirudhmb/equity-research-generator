# System Architecture

## Overview

**Automated Equity Research Report Generator** using **LangGraph StateGraph** with a 3-node sequential workflow powered by LangChain and free LLMs (Groq/Gemini).

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                       (Streamlit Web UI)                        │
│                                                                 │
│  Input: Company Ticker  →  Output: Word Doc + Excel File       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   LANGGRAPH STATEGRAPH                          │
│              (Sequential Workflow with Shared State)            │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │         EquityResearchState (Shared State)              │  │
│   │  • ticker, company_name                                 │  │
│   │  • company_info, stock_prices, financials               │  │
│   │  • ratios, beta, cost_of_equity, ddm_valuation         │  │
│   │  • executive_summary, analysis_text, report_sections    │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│   ┌──────────────────────────────────────────┐                 │
│   │  Node 1: collect_data_node()             │                 │
│   │  (Deterministic - No LLM)                │                 │
│   │  • Fetches all data from tools           │                 │
│   │  • Updates state with raw data           │                 │
│   └──────────────────────────────────────────┘                 │
│                              ↓                                  │
│   ┌──────────────────────────────────────────┐                 │
│   │  Node 2: analyze_node()                  │                 │
│   │  (Deterministic - No LLM)                │                 │
│   │  • Calculates 18 ratios                  │                 │
│   │  • Beta, CAPM, DDM valuation             │                 │
│   │  • Updates state with analysis           │                 │
│   └──────────────────────────────────────────┘                 │
│                              ↓                                  │
│   ┌──────────────────────────────────────────┐                 │
│   │  Node 3: write_report_node()             │                 │
│   │  (LLM-Powered Agent)                     │                 │
│   │  • Synthesizes insights with LLM         │                 │
│   │  • Generates report text                 │                 │
│   │  • Updates state with report sections    │                 │
│   └──────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT GENERATION                          │
│              Word Report + Excel Workbook                       │
│              (Generated from Final State)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## LangGraph State Management

### EquityResearchState (Shared State Schema)

```python
from typing import TypedDict, Optional, Dict, List, Any
import pandas as pd

class EquityResearchState(TypedDict):
    """
    Unified state that flows through all nodes.
    Each node reads from and updates this shared state.
    """
    # === INPUT ===
    ticker: str                              # "RELIANCE"
    company_name: Optional[str]              # "Reliance Industries"
    
    # === NODE 1 OUTPUT: Data Collection ===
    company_info: Optional[Dict[str, Any]]   # Company metadata
    stock_prices: Optional[pd.DataFrame]     # 6 years historical prices
    financial_statements: Optional[Dict]     # BS, IS, CF (4 years)
    dividends: Optional[pd.DataFrame]        # Dividend history
    market_index: Optional[pd.DataFrame]     # NIFTY 50 data
    news: Optional[pd.DataFrame]             # News articles (2-3 months)
    news_categorized: Optional[Dict]         # Categorized news
    news_timeline: Optional[Dict]            # Timeline statistics
    data_quality_score: Optional[float]      # 0-1 quality score
    
    # === NODE 2 OUTPUT: Financial Analysis ===
    ratios: Optional[Dict[str, Dict]]        # 18 financial ratios
    ratio_trends: Optional[Dict]             # Trend analysis
    beta: Optional[float]                    # Systematic risk
    correlation_with_market: Optional[float] # vs NIFTY 50
    cost_of_equity: Optional[float]          # CAPM result
    ddm_valuation: Optional[Dict]            # DDM fair value
    market_risk_premium: Optional[Dict]      # Market analysis
    valuation_recommendation: Optional[str]  # Buy/Hold/Sell
    
    # === NODE 3 OUTPUT: Report Writing ===
    executive_summary: Optional[str]         # High-level overview
    company_overview_text: Optional[str]     # Company description
    financial_analysis_text: Optional[str]   # Analysis commentary
    ratio_commentary: Optional[Dict]         # Per-ratio commentary
    valuation_text: Optional[str]            # Valuation analysis
    risk_analysis_text: Optional[str]        # Risk assessment
    recent_developments_text: Optional[str]  # News synthesis
    recommendation_text: Optional[str]       # Final recommendation
    
    # === METADATA ===
    current_step: str                        # Current workflow step
    errors: List[str]                        # Error messages
    warnings: List[str]                      # Warning messages
    collection_timestamp: Optional[str]      # ISO timestamp
    processing_duration: Optional[float]     # Seconds
    data_complete: bool                      # All critical data present?
```

**Key Design Principles:**
- ✅ **Single Source of Truth**: One state object for entire workflow
- ✅ **Immutable Updates**: Nodes return updates to merge, don't modify directly
- ✅ **Type Safety**: TypedDict provides IDE autocomplete and validation
- ✅ **Organized Sections**: Clear separation by workflow stage
- ✅ **Optional Fields**: Graceful handling of missing/failed data

---

## Node Architecture

### Node 1: Data Collection Node 📊

**Type:** Deterministic Function (No LLM)

**Purpose:** Fetch all required data from various free sources

**Input:** `EquityResearchState` with `ticker` and `company_name`

**Process:**
```python
def collect_data_node(state: EquityResearchState) -> dict:
    """
    Deterministic data collection - no reasoning needed.
    Fixed workflow: fetch data in predefined order.
    """
    ticker_symbol = f"{state['ticker']}.NS"  # Add NSE suffix
    
    # 1. Company Info (yfinance)
    company_info = fetch_company_info(ticker_symbol)
    
    # 2. Stock Prices (yfinance, 6 years for beta)
    stock_prices = fetch_stock_prices(ticker_symbol, years=6)
    
    # 3. Financial Statements (yfinance, 4 years)
    statements = fetch_financial_statements(ticker_symbol, years=6)
    
    # 4. Dividends (yfinance)
    dividends = fetch_dividends(ticker_symbol)
    
    # 5. Market Index - NIFTY 50 (yfinance)
    market_index = fetch_market_index("^NSEI", years=6)
    
    # 6. News (Google News RSS + MoneyControl)
    news = fetch_all_news(state['company_name'], state['ticker'])
    
    # 7. Calculate data quality score
    quality_score = calculate_quality(...)
    
    # Return state updates (merged into shared state)
    return {
        'company_info': company_info,
        'stock_prices': stock_prices,
        'financial_statements': statements,
        'dividends': dividends,
        'market_index': market_index,
        'news': news,
        'data_quality_score': quality_score,
        'current_step': 'data_collection_complete'
    }
```

**Tools Used:**
- `tools/data_tools.py`: fetch_company_info, fetch_stock_prices, fetch_financial_statements, fetch_dividends, fetch_market_index
- `tools/news_scraper.py`: fetch_all_news, categorize_news, get_news_timeline

**Output:** State updates with all raw data

**Error Handling:** Continues on non-critical failures, logs errors in state

---

### Node 2: Financial Analysis Node 📈

**Type:** Deterministic Function (No LLM)

**Purpose:** Perform all financial calculations and valuations

**Input:** `EquityResearchState` with collected data

**Process:**
```python
def analyze_node(state: EquityResearchState) -> dict:
    """
    Deterministic calculations - pure math, no LLM.
    """
    # 1. Financial Ratios (18 ratios)
    calculator = RatioCalculator(state['financial_statements'])
    ratios = calculator.calculate_all_ratios()
    trends = calculator.calculate_trends()
    
    # 2. Beta Calculation (vs NIFTY 50)
    beta_result = calculate_beta(
        state['stock_prices'],
        state['market_index']
    )
    
    # 3. CAPM Cost of Equity
    cost_of_equity = calculate_capm_cost_of_equity(
        beta=beta_result['beta'],
        risk_free_rate=0.0725,  # Indian 10Y G-Sec
        market_return=0.13       # NIFTY 50 expected
    )
    
    # 4. DDM Valuation (if dividends exist)
    if state['dividends'] is not None:
        current_price = state['stock_prices']['Close'].iloc[-1]
        ddm_result = dividend_discount_model(
            state['dividends'],
            cost_of_equity,
            current_price=current_price
        )
    
    # Return state updates
    return {
        'ratios': ratios,
        'ratio_trends': trends,
        'beta': beta_result['beta'],
        'correlation_with_market': beta_result['correlation'],
        'cost_of_equity': cost_of_equity,
        'ddm_valuation': ddm_result,
        'valuation_recommendation': ddm_result.get('recommendation'),
        'current_step': 'analysis_complete'
    }
```

**Tools Used:**
- `tools/ratio_calculator.py`: RatioCalculator class (18 ratios)
- `tools/market_tools.py`: calculate_beta, calculate_capm_cost_of_equity, dividend_discount_model

**Output:** State updates with all calculations

**Characteristics:**
- ✅ Pure calculations - deterministic output
- ✅ No LLM needed - cost-effective
- ✅ Fast execution (< 5 seconds)

---

### Node 3: Report Writing Agent Node ✍️

**Type:** LLM-Powered Agent (Groq/Gemini)

**Purpose:** Synthesize insights and generate report text

**Input:** `EquityResearchState` with complete data and analysis

**Process:**
```python
def write_report_node(state: EquityResearchState, llm) -> dict:
    """
    LLM-powered synthesis - generates human-readable text.
    ONLY node that uses LLM for reasoning and generation.
    """
    # 1. Executive Summary
    summary_prompt = build_executive_summary_prompt(state)
    executive_summary = llm.invoke(summary_prompt).content
    
    # 2. Financial Analysis Commentary
    analysis_prompt = build_financial_analysis_prompt(state)
    financial_analysis_text = llm.invoke(analysis_prompt).content
    
    # 3. Valuation Analysis
    valuation_prompt = build_valuation_prompt(state)
    valuation_text = llm.invoke(valuation_prompt).content
    
    # 4. Recent Developments Synthesis
    if state['news'] is not None:
        developments_prompt = build_developments_prompt(state)
        recent_developments_text = llm.invoke(developments_prompt).content
    
    # 5. Risk Analysis
    risk_prompt = build_risk_analysis_prompt(state)
    risk_analysis_text = llm.invoke(risk_prompt).content
    
    # Return state updates
    return {
        'executive_summary': executive_summary,
        'financial_analysis_text': financial_analysis_text,
        'valuation_text': valuation_text,
        'recent_developments_text': recent_developments_text,
        'risk_analysis_text': risk_analysis_text,
        'current_step': 'report_writing_complete'
    }
```

**LLM Configuration:**
```python
# Free LLM Options
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)
# OR
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    api_key=os.getenv("GEMINI_API_KEY")
)
```

**Prompt Templates:** Defined in `agents/prompts.py`

**Output:** State updates with all report text sections

**Characteristics:**
- ✅ Uses LLM for synthesis and generation
- ✅ Data-driven prompts (all data from state)
- ✅ Professional, objective tone
- ✅ No hallucinations (grounded in state data)

---

## Workflow Execution

### Graph Definition

```python
from langgraph.graph import StateGraph

def create_research_graph():
    """Create the LangGraph workflow."""
    # Initialize graph with state schema
    graph = StateGraph(EquityResearchState)
    
    # Add nodes
    graph.add_node("collect_data", collect_data_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("write_report", write_report_node)
    
    # Define sequential workflow
    graph.set_entry_point("collect_data")
    graph.add_edge("collect_data", "analyze")
    graph.add_edge("analyze", "write_report")
    graph.set_finish_point("write_report")
    
    # Compile graph
    return graph.compile()
```

### Execution Flow

```python
# Create graph
app = create_research_graph()

# Initial state
initial_state = {
    'ticker': 'RELIANCE',
    'company_name': 'Reliance Industries',
    'errors': [],
    'warnings': [],
    'current_step': 'start',
    'data_complete': False
}

# Run workflow (state flows through all nodes)
final_state = app.invoke(initial_state)

# Final state contains:
# - All raw data (node 1)
# - All calculations (node 2)
# - All report text (node 3)
# - Metadata (errors, warnings, timestamps)
```

---

## Data Flow Diagram

```
INPUT STATE
├── ticker: "RELIANCE"
└── company_name: "Reliance Industries"
        ↓
┌─────────────────────────┐
│ collect_data_node()     │ → Updates state with:
│ (5-10 seconds)          │   • company_info
└─────────────────────────┘   • stock_prices (1,486 days)
        ↓                     • financial_statements (4 years)
STATE UPDATE                  • dividends (30 payments)
        ↓                     • market_index (NIFTY 50)
┌─────────────────────────┐   • news (114 articles)
│ analyze_node()          │ → Updates state with:
│ (2-5 seconds)           │   • ratios (18 ratios × 4 years)
└─────────────────────────┘   • beta (1.101)
        ↓                     • cost_of_equity (13.58%)
STATE UPDATE                  • ddm_valuation (₹380.70)
        ↓
┌─────────────────────────┐
│ write_report_node()     │ → Updates state with:
│ (30-60 seconds)         │   • executive_summary
└─────────────────────────┘   • financial_analysis_text
        ↓                     • valuation_text
FINAL STATE                   • risk_analysis_text
                              • recent_developments_text
```

---

## Technology Stack

### Core Framework
- **LangGraph**: StateGraph for workflow orchestration
- **LangChain**: Agent framework and LLM integration
- **Python 3.10+**: Core language

### LLMs (Free Options)
- **Groq API**: llama-3.1-70b-versatile (Free tier: 30 req/min)
- **Google Gemini**: gemini-1.5-flash (Free tier: 15 req/min)
- **Local Ollama**: Optional for complete offline operation

### Data Sources (All Free)
- **yfinance**: Financial data, stock prices, dividends
- **Google News RSS**: News articles (2-3 months)
- **MoneyControl**: Additional Indian market news
- **NSE India**: Company information

### Python Libraries
```
langgraph>=0.0.20
langchain>=0.1.0
langchain-groq
langchain-google-genai
yfinance
pandas
numpy
scipy
beautifulsoup4
requests
feedparser
python-docx
openpyxl
streamlit
```

---

## File Structure

```
Assignment/
├── agents/
│   ├── __init__.py
│   ├── state.py                    # EquityResearchState schema
│   ├── graph.py                    # StateGraph definition
│   ├── llm_config.py              # LLM configuration
│   ├── prompts.py                 # LLM prompt templates
│   └── nodes/
│       ├── __init__.py
│       ├── data_collection.py      # Node 1 (deterministic)
│       ├── financial_analysis.py   # Node 2 (deterministic)
│       └── report_writing.py       # Node 3 (LLM-powered)
│
├── tools/                          # Reusable tool functions
│   ├── data_tools.py              # yfinance wrappers
│   ├── ratio_calculator.py        # 18 financial ratios
│   ├── market_tools.py            # Beta, CAPM, DDM
│   └── news_scraper.py            # News aggregation
│
├── config/
│   ├── settings.py                # Configuration
│   └── env_template.txt           # Environment template
│
├── utils/
│   └── logger.py                  # Logging utility
│
├── tests/
│   ├── test_data_collection_node.py
│   ├── test_financial_analysis_node.py
│   ├── test_report_writing_node.py
│   └── test_integration.py        # End-to-end tests
│
├── ui/
│   └── app.py                     # Streamlit interface
│
├── data/                          # Generated CSV files
├── outputs/                       # Generated reports
└── docs/                          # Documentation
```

---

## Performance Characteristics

### Execution Time (Per Company)
- **Node 1 (Data Collection)**: 5-10 seconds
- **Node 2 (Financial Analysis)**: 2-5 seconds
- **Node 3 (Report Writing)**: 30-60 seconds (LLM calls)
- **Total**: ~40-75 seconds per company

### Cost
- **Data Acquisition**: Free (yfinance, Google News)
- **Calculations**: Free (local Python)
- **LLM Calls**: Free (Groq/Gemini free tier)
- **Total**: $0.00 per report ✅

### Resource Requirements
- **RAM**: 2-4 GB (without local LLM)
- **CPU**: Minimal (mostly I/O bound)
- **Network**: Required for data fetching
- **Storage**: ~10 MB per company report

---

## Error Handling & Resilience

### Node-Level Error Handling
```python
def collect_data_node(state):
    updates = {'errors': [], 'warnings': []}
    
    try:
        company_info = fetch_company_info(...)
        updates['company_info'] = company_info
    except Exception as e:
        updates['errors'].append(f"Company info: {str(e)}")
        # Continue execution - don't fail entire workflow
    
    # ... more data collection with individual try/except
    
    return updates
```

### Data Quality Scoring
- Each node calculates quality score (0-1)
- Workflow continues even with partial data
- Final report includes data completeness disclaimer

### State Validation
- Type checking with TypedDict
- Optional fields for graceful degradation
- Error/warning lists tracked in state

---

## Advantages of This Architecture

### 1. **Proper LangGraph Implementation** ✅
- State-first design (best practice)
- Sequential workflow with clear dependencies
- Single source of truth (one state object)

### 2. **Cost-Effective** 💰
- LLM only used for synthesis (Node 3)
- Nodes 1 & 2 are pure Python (free)
- 100% free data sources

### 3. **Fast & Efficient** ⚡
- Deterministic nodes execute quickly
- No unnecessary LLM calls
- Parallel data fetching within nodes

### 4. **Maintainable** 🔧
- Clear separation of concerns
- Each node has single responsibility
- Easy to test individually

### 5. **Scalable** 📈
- Can process multiple companies in parallel
- State-based design allows easy batching
- Modular architecture

### 6. **Robust** 🛡️
- Graceful error handling
- Continues on partial failures
- Data quality tracking

---

## Future Enhancements

### Potential Additions
1. **Conditional Routing**: Skip DDM if no dividends, use alternative valuation
2. **Parallel Data Fetching**: Fetch financial data and news simultaneously
3. **Caching**: Cache market index data (NIFTY 50) for multiple companies
4. **Batch Processing**: Process multiple companies in one graph execution
5. **Human-in-the-Loop**: Add approval node before report generation
6. **Multi-Model Ensemble**: Use multiple LLMs and synthesize results

### LangGraph Features to Explore
- `add_conditional_edges()`: Dynamic routing based on state
- `checkpointer`: Save intermediate states for resume capability
- `parallel()`: Execute nodes concurrently
- `subgraphs`: Modular sub-workflows

---

## Comparison: Old vs New Architecture

| Aspect | Old (Incorrect) | New (Correct LangGraph) |
|--------|----------------|------------------------|
| **State** | 3 separate states per agent | 1 unified EquityResearchState |
| **Flow** | Parallel agents, unclear coordination | Sequential nodes, clear flow |
| **Agent Type** | 3 agent classes | 3 node functions |
| **LLM Usage** | Potentially all agents | Only Node 3 (writing) |
| **State Management** | Manual orchestration | LangGraph StateGraph |
| **Testing** | Test 3 separate agents | Test 3 nodes + full graph |
| **Cost** | Higher (more LLM calls) | Lower (minimal LLM use) |
| **Speed** | Slower (agent overhead) | Faster (direct functions) |
| **Maintainability** | Complex agent interactions | Simple sequential flow |

---

## Conclusion

This architecture follows **LangGraph best practices** with:
- ✅ State-first design
- ✅ Clear sequential workflow
- ✅ Minimal LLM usage (cost-effective)
- ✅ Proper use of StateGraph
- ✅ Type-safe state management
- ✅ Modular, testable components

The result is a **fast, cost-effective, and maintainable** system for automated equity research report generation! 🚀
