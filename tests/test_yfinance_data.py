"""
Test script to validate yfinance data acquisition for Indian companies.

This script tests:
1. Stock price data availability
2. Financial statements (Income, Balance Sheet, Cash Flow)
3. Company information
4. Dividend history
5. NIFTY 50 benchmark data
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DEFAULT_MARKET_INDEX, get_ticker_with_suffix
from utils.logger import logger


def test_company_data(ticker: str, exchange: str = "NSE"):
    """
    Test data acquisition for a single company.
    
    Args:
        ticker: Base ticker symbol (e.g., "RELIANCE")
        exchange: Exchange name ("NSE" or "BSE")
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing {ticker} on {exchange}")
    logger.info(f"{'='*60}")
    
    # Get ticker with suffix
    full_ticker = get_ticker_with_suffix(ticker, exchange)
    logger.info(f"Full ticker: {full_ticker}")
    
    try:
        # Create ticker object
        stock = yf.Ticker(full_ticker)
        
        # Test 1: Company Info
        logger.info("\n📋 Test 1: Company Information")
        info = stock.info
        if info:
            logger.success(f"✅ Company Name: {info.get('longName', 'N/A')}")
            logger.success(f"✅ Sector: {info.get('sector', 'N/A')}")
            logger.success(f"✅ Industry: {info.get('industry', 'N/A')}")
            logger.success(f"✅ Market Cap: ₹{info.get('marketCap', 0):,.0f}")
            logger.success(f"✅ PE Ratio: {info.get('trailingPE', 'N/A')}")
        else:
            logger.error("❌ No company info available")
            return False
        
        # Test 2: Historical Prices
        logger.info("\n📈 Test 2: Historical Stock Prices (5 years)")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        hist = stock.history(start=start_date, end=end_date)
        
        if not hist.empty:
            logger.success(f"✅ Retrieved {len(hist)} days of price data")
            logger.success(f"✅ Date Range: {hist.index[0].date()} to {hist.index[-1].date()}")
            logger.success(f"✅ Latest Close: ₹{hist['Close'].iloc[-1]:.2f}")
            logger.success(f"✅ 52-Week High: ₹{hist['High'].tail(252).max():.2f}")
            logger.success(f"✅ 52-Week Low: ₹{hist['Low'].tail(252).min():.2f}")
        else:
            logger.error("❌ No historical price data available")
            return False
        
        # Test 3: Financial Statements
        logger.info("\n💰 Test 3: Financial Statements")
        
        # Income Statement
        income_stmt = stock.financials
        if not income_stmt.empty:
            logger.success(f"✅ Income Statement: {len(income_stmt.columns)} periods")
            logger.success(f"   Available metrics: {len(income_stmt)} line items")
            if 'Total Revenue' in income_stmt.index:
                revenue = income_stmt.loc['Total Revenue'].iloc[0]
                logger.success(f"   Latest Revenue: ₹{revenue:,.0f}")
        else:
            logger.warning("⚠️ Income statement data limited/unavailable")
        
        # Balance Sheet
        balance_sheet = stock.balance_sheet
        if not balance_sheet.empty:
            logger.success(f"✅ Balance Sheet: {len(balance_sheet.columns)} periods")
            logger.success(f"   Available metrics: {len(balance_sheet)} line items")
        else:
            logger.warning("⚠️ Balance sheet data limited/unavailable")
        
        # Cash Flow
        cash_flow = stock.cashflow
        if not cash_flow.empty:
            logger.success(f"✅ Cash Flow: {len(cash_flow.columns)} periods")
            logger.success(f"   Available metrics: {len(cash_flow)} line items")
        else:
            logger.warning("⚠️ Cash flow data limited/unavailable")
        
        # Test 4: Dividends
        logger.info("\n💵 Test 4: Dividend History")
        dividends = stock.dividends
        if not dividends.empty:
            logger.success(f"✅ Dividend History: {len(dividends)} payments")
            recent_divs = dividends.tail(5)
            logger.success(f"✅ Recent dividends (last 5):")
            for date, amount in recent_divs.items():
                logger.success(f"   {date.date()}: ₹{amount:.2f}")
        else:
            logger.info("ℹ️ No dividend history (company may not pay dividends)")
        
        # Test 5: Quarterly Data
        logger.info("\n📊 Test 5: Quarterly Financials")
        quarterly_income = stock.quarterly_financials
        if not quarterly_income.empty:
            logger.success(f"✅ Quarterly Income: {len(quarterly_income.columns)} quarters")
        else:
            logger.warning("⚠️ Quarterly financial data limited/unavailable")
        
        logger.success(f"\n✅ {ticker} ({exchange}) - Data acquisition successful!\n")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Error testing {ticker}: {str(e)}\n")
        return False


def test_market_index():
    """Test NIFTY 50 index data acquisition."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing Market Benchmark: {DEFAULT_MARKET_INDEX} (NIFTY 50)")
    logger.info(f"{'='*60}")
    
    try:
        nifty = yf.Ticker(DEFAULT_MARKET_INDEX)
        
        # Get 5 years of index data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        hist = nifty.history(start=start_date, end=end_date)
        
        if not hist.empty:
            logger.success(f"✅ Retrieved {len(hist)} days of NIFTY 50 data")
            logger.success(f"✅ Date Range: {hist.index[0].date()} to {hist.index[-1].date()}")
            logger.success(f"✅ Current Level: {hist['Close'].iloc[-1]:.2f}")
            
            # Calculate returns
            returns = hist['Close'].pct_change().dropna()
            annual_return = (1 + returns.mean())**252 - 1
            logger.success(f"✅ Annualized Return: {annual_return:.2%}")
            logger.success(f"✅ Volatility (StdDev): {returns.std() * (252**0.5):.2%}")
            
            return True
        else:
            logger.error("❌ No NIFTY 50 data available")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing NIFTY 50: {str(e)}")
        return False


def main():
    """Run all data acquisition tests."""
    logger.info("=" * 80)
    logger.info("YFINANCE DATA ACQUISITION TEST - INDIAN MARKETS")
    logger.info("=" * 80)
    
    # Test companies (diverse sectors)
    test_companies = [
        ("RELIANCE", "NSE"),   # Oil & Gas / Telecom / Retail
        ("TCS", "NSE"),        # IT Services
        ("INFY", "NSE"),       # IT Services
        ("HDFCBANK", "NSE"),   # Banking
        ("ITC", "NSE"),        # FMCG / Tobacco
    ]
    
    results = {}
    
    # Test market index first
    logger.info("\n🏛️ Testing Market Benchmark...")
    results['NIFTY50'] = test_market_index()
    
    # Test individual companies
    logger.info("\n🏢 Testing Individual Companies...")
    for ticker, exchange in test_companies:
        results[ticker] = test_company_data(ticker, exchange)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {name}")
    
    logger.info(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.success("\n🎉 All data acquisition tests passed!")
        logger.info("\n💡 Next Steps:")
        logger.info("   1. Create data collection tools (tools/data_tools.py)")
        logger.info("   2. Implement financial ratio calculations")
        logger.info("   3. Build the three agents (Data, Analysis, Research)")
    else:
        logger.warning(f"\n⚠️ {total - passed} test(s) failed. Review data sources.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

