"""
Configuration settings for Equity Research Report Generator.

This module loads environment variables and provides configuration
for the entire application.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# ==================== LLM Configuration ====================

# LLM Provider (groq, ollama, or gemini)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.3"))

# Ollama Configuration (Alternative)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Gemini Configuration (Alternative)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")

# ==================== Indian Market Configuration ====================

# Market Benchmark
DEFAULT_MARKET_INDEX = os.getenv("DEFAULT_MARKET_INDEX", "^NSEI")  # NIFTY 50

# Financial Parameters (Indian Markets)
RISK_FREE_RATE = float(os.getenv("RISK_FREE_RATE", "0.0725"))  # 7.25% G-Sec
EXPECTED_MARKET_RETURN = float(os.getenv("EXPECTED_MARKET_RETURN", "0.13"))  # 13%

# Market Risk Premium (calculated)
MARKET_RISK_PREMIUM = EXPECTED_MARKET_RETURN - RISK_FREE_RATE

# Exchange Suffixes
NSE_SUFFIX = os.getenv("NSE_SUFFIX", ".NS")  # National Stock Exchange
BSE_SUFFIX = os.getenv("BSE_SUFFIX", ".BO")  # Bombay Stock Exchange

# ==================== Data Configuration ====================

# Time Periods
YEARS_OF_DATA = int(os.getenv("YEARS_OF_DATA", "5"))
MONTHS_OF_NEWS = int(os.getenv("MONTHS_OF_NEWS", "12"))

# Data Sources
NEWS_SOURCES = [
    "https://www.moneycontrol.com",
    "https://economictimes.indiatimes.com",
    "https://www.nseindia.com"
]

# ==================== System Configuration ====================

# Retry Logic
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ==================== Directory Paths ====================

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# ==================== Financial Ratios Configuration ====================

# Minimum required ratios (as per assignment)
REQUIRED_RATIOS = {
    "liquidity": ["current_ratio", "cash_ratio"],
    "efficiency": ["asset_turnover", "inventory_turnover", "receivables_turnover"],
    "solvency": ["debt_to_equity", "interest_coverage"],
    "profitability": ["net_profit_margin", "roe", "roa", "gross_margin"]
}

# ==================== Document Generation Settings ====================

# Report Template
REPORT_TEMPLATE = TEMPLATES_DIR / "Equity Research Report-Template.docx"

# File Naming
REPORT_FILENAME_TEMPLATE = "{company_name}_Equity_Research_{date}.docx"
EXCEL_FILENAME_TEMPLATE = "{company_name}_Financial_Analysis_{date}.xlsx"

# ==================== Validation ====================

def validate_config() -> tuple[bool, list[str]]:
    """
    Validate that all required configuration is set.
    
    Returns:
        tuple: (is_valid, list of errors)
    """
    errors = []
    
    # Check LLM Provider is set correctly
    if LLM_PROVIDER not in ["groq", "ollama", "gemini"]:
        errors.append(f"Invalid LLM_PROVIDER: {LLM_PROVIDER}. Must be 'groq', 'ollama', or 'gemini'")
    
    # Check Groq API key if using Groq
    if LLM_PROVIDER == "groq" and not GROQ_API_KEY:
        errors.append("GROQ_API_KEY not set. Get one at: https://console.groq.com/")
    
    # Check Gemini API key if using Gemini
    if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY not set. Get one at: https://makersuite.google.com/")
    
    # Validate financial parameters
    if not (0 < RISK_FREE_RATE < 1):
        errors.append(f"Invalid RISK_FREE_RATE: {RISK_FREE_RATE}. Should be between 0 and 1 (e.g., 0.0725 for 7.25%)")
    
    if not (0 < EXPECTED_MARKET_RETURN < 1):
        errors.append(f"Invalid EXPECTED_MARKET_RETURN: {EXPECTED_MARKET_RETURN}. Should be between 0 and 1 (e.g., 0.13 for 13%)")
    
    # Check report template exists
    if not REPORT_TEMPLATE.exists():
        errors.append(f"Report template not found: {REPORT_TEMPLATE}")
    
    return len(errors) == 0, errors


def get_llm():
    """
    Get the configured LLM instance.
    
    Returns:
        LLM instance configured based on LLM_PROVIDER setting
    """
    if LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=GROQ_TEMPERATURE
        )
    elif LLM_PROVIDER == "ollama":
        from langchain_ollama import OllamaLLM
        return OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL
        )
    elif LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            google_api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")


def get_ticker_with_suffix(ticker: str, exchange: str = "NSE") -> str:
    """
    Add appropriate suffix to ticker based on exchange.
    
    Args:
        ticker: Base ticker symbol (e.g., "RELIANCE")
        exchange: Exchange name ("NSE" or "BSE")
    
    Returns:
        Ticker with suffix (e.g., "RELIANCE.NS")
    """
    # If ticker already has suffix, return as is
    if ticker.endswith(NSE_SUFFIX) or ticker.endswith(BSE_SUFFIX):
        return ticker
    
    # Add appropriate suffix
    if exchange.upper() == "NSE":
        return f"{ticker}{NSE_SUFFIX}"
    elif exchange.upper() == "BSE":
        return f"{ticker}{BSE_SUFFIX}"
    else:
        # Default to NSE
        return f"{ticker}{NSE_SUFFIX}"


# ==================== Display Configuration ====================

def print_config():
    """Print current configuration (for debugging)."""
    print("=" * 60)
    print("EQUITY RESEARCH GENERATOR - CONFIGURATION")
    print("=" * 60)
    print(f"\n🤖 LLM Configuration:")
    print(f"   Provider: {LLM_PROVIDER}")
    if LLM_PROVIDER == "groq":
        print(f"   Model: {GROQ_MODEL}")
        print(f"   API Key: {'✅ Set' if GROQ_API_KEY else '❌ Not Set'}")
    elif LLM_PROVIDER == "ollama":
        print(f"   Model: {OLLAMA_MODEL}")
        print(f"   Base URL: {OLLAMA_BASE_URL}")
    elif LLM_PROVIDER == "gemini":
        print(f"   Model: {GEMINI_MODEL}")
        print(f"   API Key: {'✅ Set' if GEMINI_API_KEY else '❌ Not Set'}")
    
    print(f"\n🇮🇳 Indian Market Configuration:")
    print(f"   Benchmark Index: {DEFAULT_MARKET_INDEX}")
    print(f"   Risk-Free Rate: {RISK_FREE_RATE:.2%}")
    print(f"   Expected Market Return: {EXPECTED_MARKET_RETURN:.2%}")
    print(f"   Market Risk Premium: {MARKET_RISK_PREMIUM:.2%}")
    print(f"   NSE Suffix: {NSE_SUFFIX}")
    print(f"   BSE Suffix: {BSE_SUFFIX}")
    
    print(f"\n📊 Data Configuration:")
    print(f"   Years of Data: {YEARS_OF_DATA}")
    print(f"   Months of News: {MONTHS_OF_NEWS}")
    print(f"   Max Retries: {MAX_RETRIES}")
    
    print(f"\n📁 Directories:")
    print(f"   Project Root: {PROJECT_ROOT}")
    print(f"   Data: {DATA_DIR}")
    print(f"   Outputs: {OUTPUTS_DIR}")
    print(f"   Templates: {TEMPLATES_DIR}")
    
    # Validate configuration
    is_valid, errors = validate_config()
    print(f"\n✅ Configuration Status:")
    if is_valid:
        print("   ✅ All configuration valid!")
    else:
        print("   ❌ Configuration errors:")
        for error in errors:
            print(f"      - {error}")
    print("=" * 60)


if __name__ == "__main__":
    # Print configuration when run directly
    print_config()

