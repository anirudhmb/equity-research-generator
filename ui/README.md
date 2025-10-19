# 🚀 Streamlit UI for Equity Research Generator

## Overview

This is the web interface for the Automated Equity Research Report Generator. It provides a user-friendly way to generate comprehensive equity research reports for Indian publicly traded companies.

## Features

✅ **Simple Interface**: Enter a ticker and generate reports  
✅ **Progress Tracking**: Real-time progress indicators  
✅ **Key Metrics Display**: View important financial metrics instantly  
✅ **Download Options**: Get both Word (.docx) and Excel (.xlsx) reports  
✅ **Error Handling**: Clear error messages and warnings  
✅ **Indian Market Focus**: Optimized for NSE/BSE listed companies  

## Quick Start

### 1. Launch UI

From the project root:

```bash
# Option 1: Using the launcher script
python run_ui.py

# Option 2: Direct streamlit command
streamlit run ui/app.py
```

### 2. Generate a Report

1. Enter a company ticker (e.g., `RELIANCE`, `TCS`, `INFY`)
2. Optionally enter the full company name
3. Select output formats (Word, Excel, or both)
4. Click "🚀 Generate Report"
5. Wait for processing (2-5 minutes)
6. Download your reports!

## Supported Companies

- **NSE-listed companies**: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, etc.
- **BSE-listed companies**: Any BSE ticker

**Note**: Enter the ticker **without** the `.NS` or `.BO` suffix. The system will automatically detect the exchange.

## UI Components

### Main Interface

- **Ticker Input**: Enter the company symbol
- **Company Name**: Optional full name for better formatting
- **Output Options**: Choose Word report, Excel workbook, or both
- **Generate Button**: Start the report generation process

### Progress Tracking

The UI shows real-time progress:
- 🔧 Initializing workflow (10%)
- 📊 Collecting data (20-50%)
- 📝 Generating documents (70-100%)

### Key Metrics Dashboard

After generation, you'll see:
- Current stock price
- Market capitalization
- Beta (market risk)
- Cost of Equity (CAPM)
- Fair Value (DDM)
- Upside/Downside potential
- Investment recommendation
- Financial ratios (expandable)

### Downloads

Two download buttons:
- 📄 **Word Report**: Professional research report (.docx)
- 📊 **Excel Workbook**: Detailed data and calculations (.xlsx)

## Configuration

The UI reads configuration from `.env` file:

```bash
# LLM Provider (for report text generation)
LLM_PROVIDER=groq  # or gemini, ollama

# Groq API Key (free tier: https://console.groq.com)
GROQ_API_KEY=your_api_key_here

# Or Gemini API Key (free tier: https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_api_key_here
```

**Note**: If no LLM API key is configured, the UI will still work but will use placeholder text for narrative sections.

## Output Files

Generated reports are saved in the `output/` directory:

```
output/
├── Equity_Research_RELIANCE_20251019.docx      # Word report
└── Equity_Research_Data_RELIANCE_20251019.xlsx # Excel workbook
```

## Troubleshooting

### UI Won't Start

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### No Data Available

**Error**: "No stock price data available"

**Solution**: 
- Check if the ticker is correct (NSE/BSE)
- Ensure the company is actively traded
- Try a well-known ticker like `RELIANCE` first

### Report Generation Fails

**Error**: Various errors during generation

**Solution**:
1. Check your internet connection (required for data fetching)
2. Try a different company ticker
3. Check the terminal/console for detailed error logs
4. Ensure all dependencies are installed

### Download Buttons Not Working

**Error**: Files not downloading

**Solution**:
- Check browser settings (allow downloads)
- Check `output/` directory permissions
- Try a different browser

## Architecture

The UI is built with:
- **Frontend**: Streamlit (Python web framework)
- **Backend**: LangGraph workflow engine
- **Data**: yfinance, news scrapers, web scraping
- **LLM**: Groq/Gemini/Ollama (for report synthesis)
- **Output**: python-docx, openpyxl

```
┌─────────────────┐
│  Streamlit UI   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph      │
│  Workflow       │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Data   │ │ Report │
│ Nodes  │ │ Writer │
└────────┘ └────────┘
```

## Tips for Best Results

1. **Use well-known companies**: Start with large-cap companies like RELIANCE, TCS, INFY
2. **Wait patiently**: Report generation takes 2-5 minutes
3. **Check data quality**: Review the data quality score shown in the UI
4. **Read warnings**: Pay attention to any warnings about missing data
5. **Compare multiple companies**: Generate reports for peers in the same sector

## Examples

### Example 1: Reliance Industries
```
Ticker: RELIANCE
Company Name: Reliance Industries Limited
Outputs: Word ✓, Excel ✓
```

### Example 2: Tata Consultancy Services
```
Ticker: TCS
Company Name: Tata Consultancy Services
Outputs: Word ✓, Excel ✓
```

### Example 3: Infosys
```
Ticker: INFY
Company Name: Infosys Limited
Outputs: Word ✓, Excel ✓
```

## Keyboard Shortcuts

While using the UI:
- `Ctrl+C`: Stop the server
- `Cmd/Ctrl+R`: Reload the page
- `Cmd/Ctrl+Shift+R`: Hard reload (clear cache)

## Browser Compatibility

Tested on:
- ✅ Google Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Microsoft Edge

## Performance

Typical generation times:
- Data Collection: 30-60 seconds
- Financial Analysis: 10-20 seconds
- Report Writing: 20-40 seconds
- Document Generation: 10-20 seconds
- **Total**: 2-5 minutes

## Privacy & Security

- **No data is stored**: All data is fetched in real-time
- **No external uploads**: Reports are generated locally
- **API keys**: Stored in `.env` file (never shared)
- **Open source**: All code is visible and auditable

## Support

For issues or questions:
1. Check the logs in the terminal
2. Review this README
3. Check the main project README
4. Open an issue on GitHub

## License

Same as the main project. See `../LICENSE` for details.

