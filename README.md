# Automated Equity Research Report Generator 📊

An AI-powered system that automatically generates comprehensive equity research reports for **Indian publicly traded companies** (NSE/BSE) using a 3-agent architecture with LangChain, LangGraph, and **free/open-source LLMs**.

**🖥️ Cross-Platform:** Works on macOS, Windows, and Linux

---

## 🎯 Project Overview

This system automates the complete equity research report generation process as per MBA BITS Financial Management assignment requirements. Simply enter an Indian company ticker symbol and receive:

- **📄 Word Document**: Professional equity research report
- **📊 Excel Workbook**: Financial data, calculations, and analysis

**Generation Time**: ~5-10 minutes per company  
**Cost**: 100% Free - Uses open-source LLMs and free data sources  
**Markets**: NSE (National Stock Exchange) and BSE (Bombay Stock Exchange)

---

## 🏗️ Architecture

### 3-Agent System

```
User Input (Ticker)
    ↓
┌─────────────────────────────────┐
│   LangGraph Orchestrator        │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│   Agent 1: Data Collection      │
│   Fetches & prepares raw data   │
└─────────────────────────────────┘
    ↓ (CSV Files)
    ├──────────────┬───────────────┐
    ↓              ↓               ↓
┌──────────┐  ┌────────────┐  ┌──────────┐
│ Agent 2  │  │  Agent 3   │  │          │
│ Analyst  │  │  Research  │  │ Parallel │
│ Numbers  │  │  Insights  │  │          │
└──────────┘  └────────────┘  └──────────┘
    ↓              ↓
    └──────┬───────┘
           ↓
┌─────────────────────────────────┐
│   Document Generation           │
│   Word Report + Excel File      │
└─────────────────────────────────┘
```

---

## 📁 Project Structure

```
Assignment/
├── agents/              # 3 specialized agents
│   ├── data_agent.py
│   ├── analyst_agent.py
│   └── research_agent.py
│
├── tools/               # Agent tools
│   ├── data_tools.py
│   ├── analysis_tools.py
│   ├── research_tools.py
│   ├── visualization_tools.py
│   ├── excel_tools.py
│   └── document_tools.py
│
├── orchestrator/        # LangGraph workflow
│   ├── graph.py
│   └── state.py
│
├── ui/                  # Web interface
│   └── app.py
│
├── config/              # Configuration
│   └── settings.py
│
├── utils/               # Utilities
│   ├── validators.py
│   └── helpers.py
│
├── tests/               # Test suite
│
├── docs/                # Documentation
│   ├── requirements.md
│   ├── architecture.md
│   └── roadmap.md
│
├── templates/           # Original assignment files
├── data/                # Generated CSV storage
├── outputs/             # Generated reports
└── scripts/             # Utility scripts
```

---

## ✨ Features

### Automated Data Collection (Free Sources)
- ✅ 5 years of financial statements from **yfinance** (NSE/BSE)
- ✅ Historical stock prices for beta calculation
- ✅ Company information and metadata from NSE India
- ✅ Competitor analysis for Indian companies
- ✅ Recent news from MoneyControl, Economic Times

### Comprehensive Analysis (Indian Market Focus)
- ✅ **6+ Financial Ratios** (Liquidity, Efficiency, Solvency, Profitability)
- ✅ **Beta & CAPM** calculation using **NIFTY 50** as benchmark
- ✅ **DDM Valuation** using Dividend Discount Model
- ✅ **Trend Charts** for 5-year performance
- ✅ **Peer Comparison** with Indian competitors
- ✅ Uses **Indian G-Sec rate** (~7.25%) as risk-free rate

### Professional Reports
- ✅ Company overview and background
- ✅ Corporate strategy analysis
- ✅ Industry and competitor analysis
- ✅ Recent developments synthesis
- ✅ Commentary and insights
- ✅ Actionable recommendations

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** (Required)
- **Ollama installed** (Recommended - for local LLM)
  - OR Groq/Gemini API key (Free tier alternatives)
- **8GB+ RAM** (for local LLM with Ollama)
- **Internet connection** (for data fetching from NSE/BSE)

**Supported Platforms:** macOS, Windows 10/11, Linux

### Installation

#### 1. **Clone/Navigate to the repository**
```bash
# macOS/Linux
cd /path/to/equity-research-generator

# Windows
cd C:\path\to\equity-research-generator
```

#### 2. **Create virtual environment**

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### 3. **Install Ollama** (Recommended - Local & Free)

**macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh

# Then pull the model (choose one):
ollama pull llama3        # Recommended - 8B model (~4.7GB)
ollama pull mistral       # Alternative
ollama pull gemma         # Lightweight option
```

**Windows:**
1. Download from: https://ollama.com/download/windows
2. Run the installer
3. Open PowerShell/CMD and pull model:
```powershell
ollama pull llama3
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables** (Optional - only if using cloud LLMs)
```bash
cp config/env_template.txt .env
# Edit .env if using Groq/Gemini
```

**No API keys required if using Ollama!** ✅

### Usage

#### Via UI (Recommended)
```bash
streamlit run ui/app.py
```

Then:
1. Enter Indian company ticker (e.g., "RELIANCE.NS", "TCS.BO", "INFY.NS")
2. Click "Generate Report"
3. Wait ~5-10 minutes
4. Download Word document and Excel file

#### Via Python Script
```python
from orchestrator.graph import create_research_graph

# Initialize
graph = create_research_graph()

# Generate report for Indian company
result = graph.invoke({
    "ticker": "RELIANCE.NS"  # NSE ticker
    # or "RELIANCE.BO" for BSE
})

# Access outputs
word_doc = result["word_doc_path"]
excel_file = result["excel_path"]
```

---

## 📊 Sample Output

### Word Report Sections
1. **Company Overview** (100-150 words)
2. **Corporate Strategy** (bullet points)
3. **Industry & Competitor Analysis**
4. **Recent Developments**
5. **Financial Performance**
   - Ratio analysis with charts
   - Beta/CAPM analysis
   - DDM valuation
   - Commentary and insights

### Excel Workbook Sheets
1. Raw Financial Data
2. Ratio Calculations
3. Beta/CAPM Analysis
4. DDM Valuation
5. Visualizations
6. Summary

---

## 🧪 Testing

### Run Tests
```bash
pytest tests/
```

### Test Individual Components
```bash
# Test data collection
python -m tests.test_data_agent

# Test calculations
python -m tests.test_analysis_tools

# Test report generation
python -m tests.test_document_generation
```

### Manual Testing
Test with these Indian company tickers:

**NIFTY 50 Companies (NSE):**
- **IT Sector**: TCS.NS, INFY.NS, WIPRO.NS, HCLTECH.NS
- **Banking/Finance**: HDFCBANK.NS, ICICIBANK.NS, KOTAKBANK.NS
- **Energy**: RELIANCE.NS, ONGC.NS, BPCL.NS
- **FMCG**: HINDUNILVR.NS, ITC.NS, NESTLEIND.NS
- **Pharma**: SUNPHARMA.NS, DRREDDY.NS
- **Auto**: MARUTI.NS, TATAMOTORS.NS, M&M.NS

**Note**: Use `.NS` for NSE or `.BO` for BSE
Example: `RELIANCE.NS` (NSE) or `RELIANCE.BO` (BSE)

---

## 📋 Requirements Checklist

Per MBA BITS FM Assignment:

- [x] Company is NOT a bank/financial institution
- [x] 5 years of financial data
- [x] Minimum 6 ratios across all categories
- [x] Line charts for trend visualization
- [x] Commentary for each metric
- [x] Beta calculation using CAPM
- [x] DDM valuation
- [x] Corporate strategy analysis
- [x] Competitor analysis
- [x] Recent developments
- [x] Word document following template
- [x] Excel file with calculations

---

## 🛠️ Configuration

### config/settings.py

```python
# LLM Configuration (Free Options)
LLM_PROVIDER = "ollama"  # Options: "ollama", "groq", "gemini"
OLLAMA_MODEL = "llama3"  # or "mistral", "gemma"
OLLAMA_BASE_URL = "http://localhost:11434"

# Indian Market Configuration
DEFAULT_MARKET_INDEX = "^NSEI"  # NIFTY 50
RISK_FREE_RATE = 0.0725  # 7.25% - Indian 10-Year G-Sec
EXPECTED_MARKET_RETURN = 0.13  # 13% - Historical NIFTY 50

# Data Parameters
YEARS_OF_DATA = 5
MONTHS_OF_NEWS = 12

# Market Suffixes
NSE_SUFFIX = ".NS"  # National Stock Exchange
BSE_SUFFIX = ".BO"  # Bombay Stock Exchange

# Retry Logic
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
```

Customize these values based on your needs.

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Ollama connection error
- **Solution**: Ensure Ollama is running: `ollama serve`
- Check if model is pulled: `ollama list`

**Issue**: Ticker not found (yfinance)
- **Solution**: Make sure to use correct suffix:
  - NSE: `RELIANCE.NS` (not just "RELIANCE")
  - BSE: `RELIANCE.BO`
- Verify ticker exists on NSE/BSE

**Issue**: Missing financial data for Indian company
- **Solution**: Some companies have limited data on yfinance
- Try alternative ticker (NSE vs BSE)
- Check if company is recently listed

**Issue**: No dividend data (DDM fails)
- **Solution**: System provides alternative valuation notes
- Many growth companies don't pay dividends

**Issue**: Slow report generation
- **Solution**: Ollama with larger models (70B) is slower
- Use smaller model: `ollama pull llama3` (8B)
- Or switch to Groq API for faster cloud inference

---

## 📚 Documentation

- [Requirements Document](docs/requirements.md) - Detailed feature requirements
- [Architecture Document](docs/architecture.md) - System design and technical details
- [Implementation Roadmap](docs/roadmap.md) - Step-by-step development plan
- [Cross-Platform Setup](docs/CROSS_PLATFORM_SETUP.md) - Windows & macOS compatibility guide
- [Indian Markets Setup](docs/INDIAN_MARKETS_SETUP.md) - NSE/BSE specific guide

---

## 🔮 Future Enhancements

- [ ] PDF generation option
- [ ] Multiple company comparison
- [ ] Portfolio analysis
- [ ] Real-time data updates
- [ ] Custom template support
- [ ] ESG analysis
- [ ] Sentiment analysis from news

---

## 📝 License

This project is for educational purposes (MBA BITS FM Assignment).

---

## 👥 Contributors

- Abel Athur (Team Lead)
- [Add team members]

---

## 📞 Support

For questions or issues:
1. Check the [troubleshooting guide](#troubleshooting)
2. Review the [documentation](docs/)
3. Contact the team

---

## 🙏 Acknowledgments

- MBA BITS Financial Management Course
- LangChain & LangGraph frameworks
- OpenAI GPT-4
- yfinance for financial data

---

**Status**: 🚧 Under Development

**Current Phase**: Environment Setup

**Next Milestone**: Data Collection Agent

---

Made with ❤️ for MBA BITS Financial Management Assignment

