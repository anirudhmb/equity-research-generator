# Indian Markets & Free LLM Setup Guide

## 🇮🇳 Indian Market Specifics

This project is **specifically designed for Indian stock markets** (NSE/BSE) with **100% free tools**.

---

## 🎯 Key Adaptations for Indian Markets

### 1. Stock Tickers
**Format Required:**
- **NSE (National Stock Exchange)**: Add `.NS` suffix
  - Example: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`
- **BSE (Bombay Stock Exchange)**: Add `.BO` suffix
  - Example: `RELIANCE.BO`, `TCS.BO`, `INFY.BO`

**Popular NIFTY 50 Tickers:**
```
IT Sector:      TCS.NS, INFY.NS, WIPRO.NS, HCLTECH.NS
Banking:        HDFCBANK.NS, ICICIBANK.NS, KOTAKBANK.NS, SBIN.NS
Energy:         RELIANCE.NS, ONGC.NS, BPCL.NS, POWERGRID.NS
FMCG:           HINDUNILVR.NS, ITC.NS, NESTLEIND.NS
Pharma:         SUNPHARMA.NS, DRREDDY.NS, CIPLA.NS
Auto:           MARUTI.NS, TATAMOTORS.NS, M&M.NS
Telecom:        BHARTIARTL.NS, JIO.NS
```

---

### 2. Market Benchmark
**Using NIFTY 50 instead of S&P 500:**
- **Ticker**: `^NSEI` (for yfinance)
- **Historical Return**: ~12-14% annually
- **Used for**: Beta calculation and CAPM

**Alternative Indices:**
- SENSEX: `^BSESN`
- NIFTY Bank: `^NSEBANK`
- NIFTY IT: `^CNXIT`

---

### 3. Risk-Free Rate
**Indian 10-Year Government Securities (G-Sec):**
- **Current Rate**: ~7-7.5% (as of 2024)
- **Used in**: CAPM calculation for Cost of Equity

```python
# In config/settings.py
RISK_FREE_RATE = 0.0725  # 7.25%
```

**Note**: Update this periodically based on current G-Sec yields from RBI website.

---

### 4. Financial Data Source
**yfinance is FREE and works great for Indian markets!**

**📊 Data Availability:**
- ✅ **Stock Prices**: 6+ years of historical data (limited by listing date)
- ✅ **Annual Financial Statements**: 4 years of complete data (2022-2025)
- ✅ **Quarterly Financial Statements**: 6-8 quarters (~1.5-2 years)
- ✅ **Company Info**: Full metadata (sector, industry, market cap, etc.)
- ✅ **Dividends**: Complete history

**⚠️ Important Note on Financial Statements:**  
yfinance provides **4 years of complete annual financial statements** due to Yahoo Finance's data retention policy. The 5th year period often has 95%+ missing critical fields (Revenue, Net Income, Total Assets) making it unusable for ratio calculations. This limitation affects all companies globally on yfinance and is not specific to Indian markets.

**Why 4 years is sufficient:**
- ✅ Comprehensive ratio analysis and trend identification
- ✅ 5-year price history for beta calculation (separate from financials)
- ✅ Recent quarterly data for up-to-date analysis
- ✅ Meets professional equity research standards

```python
import yfinance as yf

# Get Indian company data
ticker = yf.Ticker("RELIANCE.NS")

# Available data:
- ticker.info              # Company information
- ticker.financials        # Income Statement
- ticker.balance_sheet     # Balance Sheet
- ticker.cashflow          # Cash Flow Statement
- ticker.dividends         # Dividend history
- ticker.history()         # Historical prices
```

**Data Quality for Indian Stocks:**
- ✅ Excellent: NIFTY 50 companies
- ✅ Good: NIFTY 100/200 companies
- ⚠️ Limited: Small-cap stocks
- ❌ Poor: Recently listed companies (<1 year)

---

### 5. News Sources (Free Indian Business Media)

**Primary Sources:**
1. **MoneyControl** - `https://www.moneycontrol.com`
   - Company-specific news
   - Quarterly results
   - Corporate actions

2. **Economic Times** - `https://economictimes.indiatimes.com`
   - Market analysis
   - Sector news
   - Expert opinions

3. **NSE India** - `https://www.nseindia.com`
   - Official announcements
   - Corporate filings
   - Price data

4. **Google News RSS Feeds**
   - Company-specific searches
   - Automated collection

**Implementation:**
```python
# RSS Feed example
import feedparser

company_name = "Reliance Industries"
feed_url = f"https://news.google.com/rss/search?q={company_name}"
news = feedparser.parse(feed_url)
```

---

## 🤖 Free LLM Options

### Option 1: Ollama (RECOMMENDED) ⭐

**Why Ollama?**
- ✅ 100% Free
- ✅ No API costs
- ✅ No rate limits
- ✅ Privacy (runs locally)
- ✅ Works offline
- ✅ Multiple models available

**Installation:**
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (choose one):
ollama pull llama3        # 8B - Recommended (4.7GB)
ollama pull llama3:70b    # 70B - Better quality (40GB)
ollama pull mistral       # Alternative (4GB)
ollama pull gemma         # Lightweight (2GB)
```

**System Requirements:**
- **RAM**: 8GB minimum (16GB recommended for 70B models)
- **Storage**: 5-50GB (depending on model)
- **CPU**: Any modern processor

**Usage in Project:**
```python
from langchain_ollama import OllamaLLM

llm = OllamaLLM(
    model="llama3",
    base_url="http://localhost:11434"
)
```

---

### Option 2: Groq API (Cloud Alternative)

**Why Groq?**
- ✅ Free tier: 14,400 requests/day
- ✅ Very fast inference
- ✅ No installation needed
- ✅ Access to Llama 3 70B

**Setup:**
1. Sign up: https://console.groq.com/
2. Get API key (free)
3. Add to `.env`:
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3-70b
```

**Usage in Project:**
```python
from langchain_groq import ChatGroq

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3-70b"
)
```

---

### Option 3: Google Gemini (Cloud Alternative)

**Why Gemini?**
- ✅ Free tier: 15 requests/minute, 1500/day
- ✅ Good quality
- ✅ Google infrastructure

**Setup:**
1. Get API key: https://makersuite.google.com/app/apikey
2. Add to `.env`:
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-pro
```

---

## 📊 Testing yfinance with Indian Markets

**Test Script:**
```python
import yfinance as yf
import pandas as pd

# Test 1: Get company info
print("=== Testing RELIANCE.NS ===")
reliance = yf.Ticker("RELIANCE.NS")
print(reliance.info['longName'])
print(f"Sector: {reliance.info['sector']}")
print(f"Market Cap: {reliance.info['marketCap']:,}")

# Test 2: Get financials
print("\n=== Financial Statements ===")
print(reliance.financials.head())
print(reliance.balance_sheet.head())
print(reliance.cashflow.head())

# Test 3: Get historical prices
print("\n=== Historical Prices ===")
hist = reliance.history(period="5y")
print(hist.tail())

# Test 4: Get NIFTY 50
print("\n=== NIFTY 50 Index ===")
nifty = yf.Ticker("^NSEI")
nifty_hist = nifty.history(period="5y")
print(nifty_hist.tail())

# Test 5: Calculate returns
print("\n=== Returns Calculation ===")
returns = hist['Close'].pct_change().dropna()
print(f"Mean Return: {returns.mean():.4f}")
print(f"Std Dev: {returns.std():.4f}")
```

**Expected Output:**
```
=== Testing RELIANCE.NS ===
Reliance Industries Limited
Sector: Energy
Market Cap: 16,000,000,000,000

=== Financial Statements ===
                         2023       2022       2021
Total Revenue       9200000000 8500000000 7800000000
...
```

---

## 🔧 Configuration for Indian Markets

**config/settings.py:**
```python
# Indian Market Configuration
DEFAULT_MARKET_INDEX = "^NSEI"  # NIFTY 50
RISK_FREE_RATE = 0.0725         # 7.25% G-Sec
EXPECTED_MARKET_RETURN = 0.13   # 13% historical

# Ticker Suffixes
NSE_SUFFIX = ".NS"
BSE_SUFFIX = ".BO"

# LLM Configuration
LLM_PROVIDER = "ollama"
OLLAMA_MODEL = "llama3"

# Data Sources (All Free)
NEWS_SOURCES = [
    "https://www.moneycontrol.com",
    "https://economictimes.indiatimes.com",
    "https://www.nseindia.com"
]
```

---

## ⚠️ Important Notes for Indian Markets

### 1. Financial Year Differences
- **India**: April 1 - March 31
- **Global**: January 1 - December 31
- yfinance data follows company's reporting year

### 2. Currency
- All data in **INR (Indian Rupees)**
- Market cap, revenue, etc. in Crores/Lakhs
- Be consistent in units

### 3. Data Quality
Some Indian companies have:
- Missing data for certain quarters
- Delayed reporting
- Limited historical data

**Handle gracefully with:**
- Data validation checks
- Fallback mechanisms
- Clear error messages

### 4. Market Holidays
Indian markets closed on:
- National holidays
- Special occasions
- Account for gaps in daily price data

---

## 🚀 Quick Start for Indian Markets

**1. Install Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

**2. Test yfinance:**
```bash
python3 -c "import yfinance as yf; print(yf.Ticker('TCS.NS').info['longName'])"
```

**3. Run the system:**
```bash
streamlit run ui/app.py
# Enter: RELIANCE.NS
```

---

## 📈 Recommended Test Companies

**Start with these well-documented companies:**

1. **TCS.NS** (Tata Consultancy Services)
   - Excellent data quality
   - Regular dividends
   - Stable financials

2. **RELIANCE.NS** (Reliance Industries)
   - Large cap
   - Diversified business
   - Good news coverage

3. **INFY.NS** (Infosys)
   - IT sector leader
   - Good dividend history
   - Clean financials

4. **HDFCBANK.NS** (HDFC Bank)
   - Banking sector (note: not financial institution for assignment)
   - Consistent performance
   - Good data availability

---

## 💡 Pro Tips

1. **Use NSE over BSE**: Generally better data quality on yfinance
2. **Cache Data**: Save fetched data to avoid repeated API calls
3. **Validate Tickers**: Always check if ticker exists before processing
4. **Handle INR**: Use proper formatting (Lakhs/Crores) in reports
5. **Update G-Sec Rate**: Check RBI website quarterly for current rate

---

## 🆘 Troubleshooting Indian Market Issues

**Issue**: Ticker not found
```python
# Wrong: "RELIANCE"
# Correct: "RELIANCE.NS" or "RELIANCE.BO"
```

**Issue**: No dividend data
```python
# Many growth companies don't pay dividends
# Implement alternative valuation methods
```

**Issue**: Financial data in wrong format
```python
# yfinance returns data in different currencies
# Verify currency in info['currency']
```

---

## 📚 Additional Resources

**Indian Market Data:**
- NSE India: https://www.nseindia.com
- BSE India: https://www.bseindia.com
- SEBI: https://www.sebi.gov.in
- RBI: https://www.rbi.org.in

**Free Financial APIs:**
- yfinance documentation: https://pypi.org/project/yfinance/
- NSE Python: https://github.com/jugaad-py/jugaad-data

**Free LLMs:**
- Ollama: https://ollama.ai
- Groq: https://console.groq.com
- Gemini: https://ai.google.dev

---

**This setup is 100% FREE and tailored for Indian markets! 🇮🇳🚀**

