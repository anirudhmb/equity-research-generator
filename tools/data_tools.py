"""
Financial Data Tools for Indian Market Companies.

This module provides functions to fetch and process financial data
from yfinance for Indian companies listed on NSE/BSE.
"""

import sys
from pathlib import Path
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import pandas as pd
import numpy as np
import yfinance as yf

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import (
    get_ticker_with_suffix,
    YEARS_OF_DATA,
    MAX_RETRIES,
    RETRY_DELAY,
    DEFAULT_MARKET_INDEX
)
from utils.logger import logger


def retry_on_failure(func):
    """Decorator to retry function on failure."""
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {MAX_RETRIES} attempts failed for {func.__name__}")
                    raise
    return wrapper


@retry_on_failure
def fetch_company_info(ticker: str, exchange: str = "NSE") -> Dict:
    """
    Fetch comprehensive company information.
    
    Args:
        ticker: Base ticker symbol (e.g., "RELIANCE")
        exchange: Exchange name ("NSE" or "BSE")
    
    Returns:
        Dictionary containing company information
    
    Example:
        >>> info = fetch_company_info("RELIANCE", "NSE")
        >>> print(info['longName'], info['sector'], info['marketCap'])
    """
    logger.info(f"Fetching company info for {ticker} ({exchange})")
    
    full_ticker = get_ticker_with_suffix(ticker, exchange)
    stock = yf.Ticker(full_ticker)
    info = stock.info
    
    if not info or 'longName' not in info:
        raise ValueError(f"No company info available for {full_ticker}")
    
    # Extract and clean relevant information
    company_data = {
        'ticker': ticker,
        'full_ticker': full_ticker,
        'exchange': exchange,
        'company_name': info.get('longName', 'N/A'),
        'sector': info.get('sector', 'N/A'),
        'industry': info.get('industry', 'N/A'),
        'marketCap': info.get('marketCap', 0),  # Keep camelCase to match yfinance
        'market_cap_crore': info.get('marketCap', 0) / 1e7,  # Convert to crores
        'currency': info.get('currency', 'INR'),
        'website': info.get('website', 'N/A'),
        'business_summary': info.get('longBusinessSummary', 'N/A'),
        
        # Key metrics
        'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
        'previous_close': info.get('previousClose', 0),
        'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
        'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
        
        # Valuation metrics
        'pe_ratio': info.get('trailingPE', None),
        'forward_pe': info.get('forwardPE', None),
        'pb_ratio': info.get('priceToBook', None),
        'dividend_yield': info.get('dividendYield', None),
        
        # Volume
        'avg_volume': info.get('averageVolume', 0),
        'volume': info.get('volume', 0),
        
        # Shares
        'shares_outstanding': info.get('sharesOutstanding', 0),
        'float_shares': info.get('floatShares', 0),
        
        # Additional info
        'beta': info.get('beta', None),
        'employees': info.get('fullTimeEmployees', None),
    }
    
    logger.success(f"✅ Fetched info for {company_data['company_name']}")
    return company_data


@retry_on_failure
def fetch_stock_prices(
    ticker: str,
    exchange: str = "NSE",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    years: int = YEARS_OF_DATA
) -> pd.DataFrame:
    """
    Fetch historical stock price data.
    
    Args:
        ticker: Base ticker symbol
        exchange: Exchange name
        start_date: Start date (if None, uses years parameter)
        end_date: End date (if None, uses today)
        years: Number of years of data (used if start_date is None)
    
    Returns:
        DataFrame with OHLCV data and Date as index
    
    Example:
        >>> prices = fetch_stock_prices("RELIANCE", years=5)
        >>> print(prices.head())
    """
    logger.info(f"Fetching stock prices for {ticker} ({exchange})")
    
    full_ticker = get_ticker_with_suffix(ticker, exchange)
    
    # Set date range
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=years*365)
    
    # Fetch data
    stock = yf.Ticker(full_ticker)
    hist = stock.history(start=start_date, end=end_date)
    
    if hist.empty:
        raise ValueError(f"No price data available for {full_ticker}")
    
    # Clean and prepare data
    hist.index = pd.to_datetime(hist.index)
    hist.index.name = 'Date'
    
    # Add returns
    hist['Returns'] = hist['Close'].pct_change()
    hist['Log_Returns'] = np.log(hist['Close'] / hist['Close'].shift(1))
    
    # Add moving averages
    hist['MA_50'] = hist['Close'].rolling(window=50).mean()
    hist['MA_200'] = hist['Close'].rolling(window=200).mean()
    
    logger.success(f"✅ Fetched {len(hist)} days of price data ({hist.index[0].date()} to {hist.index[-1].date()})")
    return hist


@retry_on_failure
def fetch_financial_statements(
    ticker: str,
    exchange: str = "NSE",
    quarterly: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Fetch all three financial statements.
    
    Args:
        ticker: Base ticker symbol
        exchange: Exchange name
        quarterly: If True, fetch quarterly statements; else annual
    
    Returns:
        Tuple of (income_statement, balance_sheet, cash_flow)
    
    Example:
        >>> income, balance, cashflow = fetch_financial_statements("RELIANCE")
        >>> print("Revenue:", income.loc['Total Revenue'].iloc[0])
    """
    logger.info(f"Fetching {'quarterly' if quarterly else 'annual'} financial statements for {ticker}")
    
    full_ticker = get_ticker_with_suffix(ticker, exchange)
    stock = yf.Ticker(full_ticker)
    
    # Fetch statements
    if quarterly:
        income_stmt = stock.quarterly_financials
        balance_sheet = stock.quarterly_balance_sheet
        cash_flow = stock.quarterly_cashflow
    else:
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
    
    # Clean up statements - remove columns with >90% missing data
    def clean_statement(df: pd.DataFrame, name: str) -> pd.DataFrame:
        if df.empty:
            return df
        
        # Calculate completeness for each column
        completeness = {}
        for col in df.columns:
            non_empty = df[col].notna().sum()
            total = len(df)
            completeness[col] = non_empty / total if total > 0 else 0
        
        # Keep only columns with >10% data (i.e., <90% empty)
        valid_cols = [col for col, comp in completeness.items() if comp > 0.10]
        
        if len(valid_cols) < len(df.columns):
            removed = len(df.columns) - len(valid_cols)
            logger.warning(f"Removed {removed} incomplete period(s) from {name} (>90% missing data)")
        
        return df[valid_cols] if valid_cols else df
    
    # Clean statements
    income_stmt = clean_statement(income_stmt, "Income Statement")
    balance_sheet = clean_statement(balance_sheet, "Balance Sheet")
    cash_flow = clean_statement(cash_flow, "Cash Flow")
    
    # Check if data is available
    statements_available = []
    if not income_stmt.empty and len(income_stmt.columns) > 0:
        statements_available.append(f"Income Statement ({len(income_stmt.columns)} periods)")
    if not balance_sheet.empty and len(balance_sheet.columns) > 0:
        statements_available.append(f"Balance Sheet ({len(balance_sheet.columns)} periods)")
    if not cash_flow.empty and len(cash_flow.columns) > 0:
        statements_available.append(f"Cash Flow ({len(cash_flow.columns)} periods)")
    
    if not statements_available:
        raise ValueError(f"No valid financial statements available for {full_ticker}")
    
    logger.success(f"✅ Fetched: {', '.join(statements_available)}")
    return income_stmt, balance_sheet, cash_flow


def calculate_returns_metrics(prices: pd.DataFrame) -> Dict:
    """
    Calculate return and volatility metrics from price data.
    
    Args:
        prices: DataFrame with 'Close' prices
    
    Returns:
        Dictionary with return metrics
    
    Example:
        >>> prices = fetch_stock_prices("RELIANCE")
        >>> metrics = calculate_returns_metrics(prices)
        >>> print(f"Annual Return: {metrics['annual_return']:.2%}")
    """
    logger.info("Calculating return metrics")
    
    if prices.empty or 'Close' not in prices.columns:
        raise ValueError("Price data must contain 'Close' column")
    
    # Clean data
    prices_clean = prices['Close'].dropna()
    
    if len(prices_clean) < 2:
        raise ValueError("Insufficient price data for calculations")
    
    # Daily returns
    returns = prices_clean.pct_change().dropna()
    
    # Calculate metrics
    metrics = {
        # Basic returns
        'total_return': (prices_clean.iloc[-1] / prices_clean.iloc[0]) - 1,
        'daily_return_mean': returns.mean(),
        'daily_return_std': returns.std(),
        
        # Annualized metrics (assuming 252 trading days)
        'annual_return': (1 + returns.mean())**252 - 1,
        'annual_volatility': returns.std() * np.sqrt(252),
        'sharpe_ratio': None,  # Will be calculated with risk-free rate
        
        # Additional metrics
        'min_return': returns.min(),
        'max_return': returns.max(),
        'skewness': returns.skew(),
        'kurtosis': returns.kurtosis(),
        
        # Performance metrics
        'positive_days': (returns > 0).sum(),
        'negative_days': (returns < 0).sum(),
        'win_rate': (returns > 0).sum() / len(returns),
        
        # Recent performance
        'ytd_return': None,  # Will be calculated if full year available
        'mtd_return': None,  # Will be calculated if month data available
        '1y_return': None,
        '3y_return': None,
        '5y_return': None,
    }
    
    # Calculate period returns if data available
    today = prices_clean.index[-1]
    
    # Make dates timezone-aware if needed
    if hasattr(today, 'tz') and today.tz is not None:
        # Index is timezone-aware
        year_start = pd.Timestamp(datetime(today.year, 1, 1)).tz_localize(today.tz)
        month_start = pd.Timestamp(datetime(today.year, today.month, 1)).tz_localize(today.tz)
    else:
        year_start = datetime(today.year, 1, 1)
        month_start = datetime(today.year, today.month, 1)
    
    # YTD Return
    ytd_prices = prices_clean[prices_clean.index >= year_start]
    if len(ytd_prices) > 1:
        metrics['ytd_return'] = (ytd_prices.iloc[-1] / ytd_prices.iloc[0]) - 1
    
    # MTD Return
    mtd_prices = prices_clean[prices_clean.index >= month_start]
    if len(mtd_prices) > 1:
        metrics['mtd_return'] = (mtd_prices.iloc[-1] / mtd_prices.iloc[0]) - 1
    
    # 1Y, 3Y, 5Y returns
    for years, key in [(1, '1y_return'), (3, '3y_return'), (5, '5y_return')]:
        cutoff = today - pd.Timedelta(days=years*365)
        period_prices = prices_clean[prices_clean.index >= cutoff]
        if len(period_prices) > 1:
            metrics[key] = (period_prices.iloc[-1] / period_prices.iloc[0]) - 1
    
    logger.success("✅ Calculated return metrics")
    return metrics


@retry_on_failure
def fetch_dividends(ticker: str, exchange: str = "NSE") -> pd.DataFrame:
    """
    Fetch dividend history.
    
    Args:
        ticker: Base ticker symbol
        exchange: Exchange name
    
    Returns:
        DataFrame with dividend dates and amounts
    
    Example:
        >>> divs = fetch_dividends("RELIANCE")
        >>> print(f"Total dividends: {len(divs)}")
    """
    logger.info(f"Fetching dividend history for {ticker}")
    
    full_ticker = get_ticker_with_suffix(ticker, exchange)
    stock = yf.Ticker(full_ticker)
    dividends = stock.dividends
    
    if dividends.empty:
        logger.warning(f"No dividend history for {ticker}")
        return pd.DataFrame(columns=['Date', 'Dividend'])
    
    # Convert to DataFrame
    div_df = dividends.reset_index()
    div_df.columns = ['Date', 'Dividend']
    div_df['Date'] = pd.to_datetime(div_df['Date'])
    
    logger.success(f"✅ Fetched {len(div_df)} dividend payments")
    return div_df


def calculate_dividend_metrics(dividends: pd.DataFrame, current_price: float) -> Dict:
    """
    Calculate dividend-related metrics.
    
    Args:
        dividends: DataFrame with dividend history
        current_price: Current stock price
    
    Returns:
        Dictionary with dividend metrics
    """
    logger.info("Calculating dividend metrics")
    
    if dividends.empty:
        return {
            'total_dividends': 0,
            'dividend_count': 0,
            'avg_dividend': 0,
            'latest_dividend': 0,
            'dividend_yield': 0,
            'dividend_growth_rate': None,
            'payout_frequency': 'None'
        }
    
    # Sort by date
    dividends = dividends.sort_values('Date')
    
    # Calculate metrics
    metrics = {
        'total_dividends': dividends['Dividend'].sum(),
        'dividend_count': len(dividends),
        'avg_dividend': dividends['Dividend'].mean(),
        'latest_dividend': dividends['Dividend'].iloc[-1],
        'dividend_yield': (dividends['Dividend'].iloc[-1] / current_price) if current_price > 0 else 0,
        'first_dividend_date': dividends['Date'].iloc[0],
        'latest_dividend_date': dividends['Date'].iloc[-1],
    }
    
    # Calculate dividend growth rate (if enough history)
    if len(dividends) >= 2:
        # Aggregate by year
        dividends['Year'] = dividends['Date'].dt.year
        annual_divs = dividends.groupby('Year')['Dividend'].sum()
        
        if len(annual_divs) >= 2:
            years_diff = len(annual_divs) - 1
            growth_rate = (annual_divs.iloc[-1] / annual_divs.iloc[0])**(1/years_diff) - 1
            metrics['dividend_growth_rate'] = growth_rate
        else:
            metrics['dividend_growth_rate'] = None
        
        # Estimate payout frequency
        avg_days_between = (dividends['Date'].diff().dt.days.mean())
        if avg_days_between < 120:
            metrics['payout_frequency'] = 'Quarterly'
        elif avg_days_between < 200:
            metrics['payout_frequency'] = 'Semi-Annual'
        else:
            metrics['payout_frequency'] = 'Annual'
    else:
        metrics['dividend_growth_rate'] = None
        metrics['payout_frequency'] = 'Unknown'
    
    logger.success("✅ Calculated dividend metrics")
    return metrics


@retry_on_failure
def fetch_market_index_data(
    index_ticker: str = DEFAULT_MARKET_INDEX,
    years: int = YEARS_OF_DATA
) -> pd.DataFrame:
    """
    Fetch market index data (default: NIFTY 50).
    
    Args:
        index_ticker: Index ticker symbol
        years: Number of years of data
    
    Returns:
        DataFrame with index prices and returns
    
    Example:
        >>> nifty = fetch_market_index_data()
        >>> print(f"NIFTY 50 data: {len(nifty)} days")
    """
    logger.info(f"Fetching market index data: {index_ticker}")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)
    
    index = yf.Ticker(index_ticker)
    hist = index.history(start=start_date, end=end_date)
    
    if hist.empty:
        raise ValueError(f"No data available for market index {index_ticker}")
    
    # Add returns
    hist['Returns'] = hist['Close'].pct_change()
    hist['Log_Returns'] = np.log(hist['Close'] / hist['Close'].shift(1))
    
    logger.success(f"✅ Fetched {len(hist)} days of index data")
    return hist


def get_aligned_returns(
    stock_prices: pd.DataFrame,
    market_prices: pd.DataFrame
) -> Tuple[pd.Series, pd.Series]:
    """
    Get aligned returns for stock and market (for beta calculation).
    
    Args:
        stock_prices: Stock price DataFrame
        market_prices: Market index price DataFrame
    
    Returns:
        Tuple of (stock_returns, market_returns) aligned by date
    
    Example:
        >>> stock = fetch_stock_prices("RELIANCE")
        >>> market = fetch_market_index_data()
        >>> stock_ret, market_ret = get_aligned_returns(stock, market)
        >>> print(f"Correlation: {stock_ret.corr(market_ret):.2f}")
    """
    logger.info("Aligning stock and market returns")
    
    # Get returns
    stock_returns = stock_prices['Returns'].dropna()
    market_returns = market_prices['Returns'].dropna()
    
    # Align by date (inner join)
    aligned = pd.DataFrame({
        'stock': stock_returns,
        'market': market_returns
    }).dropna()
    
    if len(aligned) < 30:
        logger.warning(f"Only {len(aligned)} aligned data points - may affect accuracy")
    
    logger.success(f"✅ Aligned {len(aligned)} return data points")
    return aligned['stock'], aligned['market']


def save_data_to_csv(data: pd.DataFrame, ticker: str, data_type: str) -> str:
    """
    Save data to CSV file in data directory.
    
    Args:
        data: DataFrame to save
        ticker: Company ticker
        data_type: Type of data (e.g., 'prices', 'financials')
    
    Returns:
        Path to saved file
    """
    from config.settings import DATA_DIR
    
    filename = f"{ticker}_{data_type}_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = DATA_DIR / filename
    
    data.to_csv(filepath)
    logger.success(f"✅ Saved {data_type} data to {filepath}")
    
    return str(filepath)


# Convenience function for complete data fetch
def fetch_all_company_data(
    ticker: str,
    exchange: str = "NSE",
    years: int = YEARS_OF_DATA,
    save_to_file: bool = False
) -> Dict:
    """
    Fetch all available data for a company.
    
    Args:
        ticker: Base ticker symbol
        exchange: Exchange name
        years: Number of years of historical data
        save_to_file: Whether to save data to CSV files
    
    Returns:
        Dictionary containing all fetched data
    
    Example:
        >>> data = fetch_all_company_data("RELIANCE", years=5)
        >>> print(f"Company: {data['info']['company_name']}")
        >>> print(f"Price points: {len(data['prices'])}")
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Fetching complete dataset for {ticker} ({exchange})")
    logger.info(f"{'='*60}")
    
    result = {
        'ticker': ticker,
        'exchange': exchange,
        'fetch_date': datetime.now()
    }
    
    try:
        # 1. Company Info
        result['info'] = fetch_company_info(ticker, exchange)
        
        # 2. Stock Prices
        result['prices'] = fetch_stock_prices(ticker, exchange, years=years)
        
        # 3. Return Metrics
        result['return_metrics'] = calculate_returns_metrics(result['prices'])
        
        # 4. Financial Statements
        income, balance, cashflow = fetch_financial_statements(ticker, exchange)
        result['income_statement'] = income
        result['balance_sheet'] = balance
        result['cash_flow'] = cashflow
        
        # 5. Quarterly Statements
        try:
            q_income, q_balance, q_cashflow = fetch_financial_statements(ticker, exchange, quarterly=True)
            result['quarterly_income'] = q_income
            result['quarterly_balance'] = q_balance
            result['quarterly_cashflow'] = q_cashflow
        except Exception as e:
            logger.warning(f"Could not fetch quarterly statements: {e}")
            result['quarterly_income'] = pd.DataFrame()
            result['quarterly_balance'] = pd.DataFrame()
            result['quarterly_cashflow'] = pd.DataFrame()
        
        # 6. Dividends
        result['dividends'] = fetch_dividends(ticker, exchange)
        result['dividend_metrics'] = calculate_dividend_metrics(
            result['dividends'],
            result['info']['current_price']
        )
        
        # 7. Market Index
        result['market_index'] = fetch_market_index_data(years=years)
        
        # Save to files if requested
        if save_to_file:
            save_data_to_csv(result['prices'], ticker, 'prices')
            if not result['income_statement'].empty:
                save_data_to_csv(result['income_statement'].T, ticker, 'income_statement')
            if not result['balance_sheet'].empty:
                save_data_to_csv(result['balance_sheet'].T, ticker, 'balance_sheet')
            if not result['cash_flow'].empty:
                save_data_to_csv(result['cash_flow'].T, ticker, 'cash_flow')
        
        logger.success(f"\n✅ Successfully fetched all data for {ticker}")
        return result
        
    except Exception as e:
        logger.error(f"\n❌ Error fetching data for {ticker}: {e}")
        raise


if __name__ == "__main__":
    # Test the module
    print("Testing Financial Data Tools...")
    
    # Test with RELIANCE
    test_ticker = "RELIANCE"
    
    try:
        data = fetch_all_company_data(test_ticker, years=6, save_to_file=True)
        print(f"\n✅ Test successful for {test_ticker}")
        print(f"Company: {data['info']['company_name']}")
        print(f"Sector: {data['info']['sector']}")
        print(f"Price points: {len(data['prices'])}")
        print(f"Annual return: {data['return_metrics']['annual_return']:.2%}")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

