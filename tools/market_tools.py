"""
Market Data Tools for Valuation and Risk Analysis.

This module provides functions for:
- Beta calculation (systematic risk vs market)
- CAPM (Capital Asset Pricing Model) for cost of equity
- DDM (Dividend Discount Model) for valuation
- Market risk premium analysis

All calculations use Indian market parameters (NIFTY 50, G-Sec rate).
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import (
    RISK_FREE_RATE,
    EXPECTED_MARKET_RETURN,
    MARKET_RISK_PREMIUM,
    DEFAULT_MARKET_INDEX
)
from utils.logger import logger


def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series, 
                   period_name: str = "full period") -> Dict:
    """
    Calculate beta (systematic risk) using linear regression.
    
    Beta measures the volatility of a stock relative to the market:
    - Beta = 1: Stock moves with market
    - Beta > 1: Stock is more volatile than market (aggressive)
    - Beta < 1: Stock is less volatile than market (defensive)
    
    Args:
        stock_returns: Stock return series
        market_returns: Market index return series
        period_name: Name for logging (e.g., "5 years")
    
    Returns:
        Dictionary with beta, alpha, R-squared, and statistics
    
    Example:
        >>> from tools.data_tools import get_aligned_returns
        >>> stock_ret, market_ret = get_aligned_returns(stock_prices, market_prices)
        >>> beta_info = calculate_beta(stock_ret, market_ret, "5 years")
        >>> print(f"Beta: {beta_info['beta']:.2f}")
    """
    logger.info(f"Calculating beta for {period_name}")
    
    # Ensure data is aligned and clean
    data = pd.DataFrame({
        'stock': stock_returns,
        'market': market_returns
    }).dropna()
    
    if len(data) < 30:
        logger.warning(f"Only {len(data)} data points - beta may be inaccurate")
    
    # Perform linear regression: stock_returns = alpha + beta * market_returns
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        data['market'], data['stock']
    )
    
    # Beta is the slope
    beta = slope
    alpha = intercept
    r_squared = r_value ** 2
    
    # Calculate additional statistics
    correlation = data['stock'].corr(data['market'])
    
    # Volatility comparison
    stock_volatility = data['stock'].std() * np.sqrt(252)  # Annualized
    market_volatility = data['market'].std() * np.sqrt(252)  # Annualized
    
    result = {
        'beta': beta,
        'alpha': alpha,
        'r_squared': r_squared,
        'correlation': correlation,
        'p_value': p_value,
        'std_error': std_err,
        'data_points': len(data),
        'stock_volatility': stock_volatility,
        'market_volatility': market_volatility,
        'interpretation': _interpret_beta(beta)
    }
    
    logger.success(f"✅ Beta calculated: {beta:.3f} ({result['interpretation']})")
    logger.debug(f"   R²: {r_squared:.3f}, Correlation: {correlation:.3f}")
    
    return result


def _interpret_beta(beta: float) -> str:
    """Get interpretation of beta value."""
    if beta > 1.2:
        return "Highly Aggressive"
    elif beta > 1.0:
        return "Aggressive"
    elif beta > 0.8:
        return "Moderately Aggressive"
    elif beta > 0.5:
        return "Defensive"
    else:
        return "Highly Defensive"


def calculate_capm_cost_of_equity(
    beta: float,
    risk_free_rate: float = RISK_FREE_RATE,
    market_return: float = EXPECTED_MARKET_RETURN
) -> Dict:
    """
    Calculate Cost of Equity using CAPM.
    
    Formula: Cost of Equity = Rf + β(Rm - Rf)
    Where:
    - Rf = Risk-free rate (Indian G-Sec rate)
    - β = Beta (systematic risk)
    - Rm = Expected market return (NIFTY 50)
    - (Rm - Rf) = Market risk premium
    
    Args:
        beta: Beta coefficient
        risk_free_rate: Risk-free rate (default: Indian G-Sec)
        market_return: Expected market return (default: NIFTY 50 historical)
    
    Returns:
        Dictionary with cost of equity and components
    
    Example:
        >>> capm = calculate_capm_cost_of_equity(beta=1.2)
        >>> print(f"Cost of Equity: {capm['cost_of_equity']:.2%}")
    """
    logger.info("Calculating CAPM cost of equity")
    
    # Calculate market risk premium
    market_risk_premium = market_return - risk_free_rate
    
    # CAPM formula
    cost_of_equity = risk_free_rate + beta * market_risk_premium
    
    result = {
        'cost_of_equity': cost_of_equity,
        'risk_free_rate': risk_free_rate,
        'beta': beta,
        'market_return': market_return,
        'market_risk_premium': market_risk_premium,
        'formula': f"{risk_free_rate:.2%} + {beta:.3f} × {market_risk_premium:.2%} = {cost_of_equity:.2%}"
    }
    
    logger.success(f"✅ Cost of Equity (CAPM): {cost_of_equity:.2%}")
    logger.debug(f"   Components: Rf={risk_free_rate:.2%}, Beta={beta:.3f}, MRP={market_risk_premium:.2%}")
    
    return result


def dividend_discount_model(
    dividends: pd.DataFrame,
    cost_of_equity: float,
    growth_rate: Optional[float] = None,
    current_price: Optional[float] = None
) -> Dict:
    """
    Calculate fair value using Dividend Discount Model (DDM).
    
    Uses Gordon Growth Model:
    Fair Value = D1 / (r - g)
    Where:
    - D1 = Next year's expected dividend
    - r = Cost of equity (required return)
    - g = Dividend growth rate
    
    Args:
        dividends: DataFrame with dividend history (columns: Date, Dividend)
        cost_of_equity: Required rate of return from CAPM
        growth_rate: Expected dividend growth rate (if None, calculated from history)
        current_price: Current stock price for valuation comparison
    
    Returns:
        Dictionary with fair value, growth rate, and recommendation
    
    Example:
        >>> from tools.data_tools import fetch_dividends, fetch_company_info
        >>> divs = fetch_dividends("RELIANCE")
        >>> info = fetch_company_info("RELIANCE")
        >>> capm = calculate_capm_cost_of_equity(1.2)
        >>> ddm = dividend_discount_model(divs, capm['cost_of_equity'], 
        ...                               current_price=info['current_price'])
        >>> print(f"Fair Value: ₹{ddm['fair_value']:.2f}")
    """
    logger.info("Calculating DDM fair value")
    
    if dividends.empty:
        logger.warning("No dividend history - DDM not applicable")
        return {
            'applicable': False,
            'reason': 'Company does not pay dividends',
            'fair_value': None
        }
    
    # Sort by date
    dividends = dividends.sort_values('Date')
    
    # Calculate growth rate if not provided
    if growth_rate is None:
        growth_rate = _calculate_dividend_growth_rate(dividends)
        logger.info(f"Calculated dividend growth rate: {growth_rate:.2%}")
    
    # Get latest dividend
    latest_dividend = dividends['Dividend'].iloc[-1]
    
    # Estimate next year's dividend
    d1 = latest_dividend * (1 + growth_rate)
    
    # Check if model is applicable
    if growth_rate >= cost_of_equity:
        logger.warning(f"Growth rate ({growth_rate:.2%}) >= Cost of Equity ({cost_of_equity:.2%}) - DDM not applicable")
        return {
            'applicable': False,
            'reason': f'Growth rate ({growth_rate:.2%}) exceeds cost of equity ({cost_of_equity:.2%})',
            'fair_value': None,
            'growth_rate': growth_rate,
            'latest_dividend': latest_dividend
        }
    
    # Gordon Growth Model
    fair_value = d1 / (cost_of_equity - growth_rate)
    
    # Calculate valuation metrics
    result = {
        'applicable': True,
        'fair_value': fair_value,
        'd0_current_dividend': latest_dividend,
        'd1_next_dividend': d1,
        'growth_rate': growth_rate,
        'cost_of_equity': cost_of_equity,
        'formula': f"₹{d1:.2f} / ({cost_of_equity:.2%} - {growth_rate:.2%}) = ₹{fair_value:.2f}"
    }
    
    # Compare with current price if provided
    if current_price:
        result['current_price'] = current_price
        result['upside_downside'] = (fair_value - current_price) / current_price
        result['recommendation'] = _get_valuation_recommendation(
            fair_value, current_price, result['upside_downside']
        )
    
    logger.success(f"✅ DDM Fair Value: ₹{fair_value:.2f}")
    if current_price:
        logger.info(f"   Current Price: ₹{current_price:.2f}")
        logger.info(f"   Upside/Downside: {result['upside_downside']:.1%}")
        logger.info(f"   Recommendation: {result['recommendation']}")
    
    return result


def _calculate_dividend_growth_rate(dividends: pd.DataFrame, years: int = 5) -> float:
    """
    Calculate historical dividend growth rate.
    
    Uses compound annual growth rate (CAGR) formula.
    """
    # Aggregate by year
    dividends['Year'] = dividends['Date'].dt.year
    annual_divs = dividends.groupby('Year')['Dividend'].sum().sort_index()
    
    if len(annual_divs) < 2:
        logger.warning("Insufficient dividend history for growth calculation")
        return 0.05  # Default 5% growth assumption
    
    # Limit to recent years
    annual_divs = annual_divs.tail(min(years, len(annual_divs)))
    
    # CAGR formula
    n_years = len(annual_divs) - 1
    if n_years == 0 or annual_divs.iloc[0] == 0:
        return 0.05
    
    cagr = (annual_divs.iloc[-1] / annual_divs.iloc[0]) ** (1 / n_years) - 1
    
    # Cap growth rate at reasonable bounds
    cagr = max(min(cagr, 0.20), -0.10)  # Between -10% and +20%
    
    return cagr


def _get_valuation_recommendation(fair_value: float, current_price: float, 
                                  upside: float) -> str:
    """Generate buy/hold/sell recommendation based on valuation."""
    if upside > 0.20:
        return "Strong Buy - Undervalued by >20%"
    elif upside > 0.10:
        return "Buy - Undervalued by >10%"
    elif upside > 0:
        return "Hold - Slightly undervalued"
    elif upside > -0.10:
        return "Hold - Fairly valued"
    elif upside > -0.20:
        return "Sell - Overvalued by >10%"
    else:
        return "Strong Sell - Overvalued by >20%"


def calculate_market_risk_premium(market_returns: pd.Series, 
                                   risk_free_rate: float = RISK_FREE_RATE) -> Dict:
    """
    Calculate market risk premium from historical data.
    
    Market Risk Premium = Average Market Return - Risk-Free Rate
    
    Args:
        market_returns: Historical market (NIFTY 50) returns
        risk_free_rate: Current risk-free rate
    
    Returns:
        Dictionary with market risk premium and statistics
    
    Example:
        >>> from tools.data_tools import fetch_market_index_data
        >>> nifty = fetch_market_index_data(years=10)
        >>> mrp = calculate_market_risk_premium(nifty['Returns'])
        >>> print(f"Market Risk Premium: {mrp['premium']:.2%}")
    """
    logger.info("Calculating market risk premium from historical data")
    
    # Clean returns
    returns = market_returns.dropna()
    
    if len(returns) < 252:
        logger.warning(f"Limited data points: {len(returns)} days")
    
    # Calculate annualized return
    avg_daily_return = returns.mean()
    annual_return = (1 + avg_daily_return) ** 252 - 1
    
    # Market risk premium
    premium = annual_return - risk_free_rate
    
    # Additional statistics
    volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility != 0 else 0
    
    result = {
        'market_return': annual_return,
        'risk_free_rate': risk_free_rate,
        'premium': premium,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'data_points': len(returns),
        'formula': f"{annual_return:.2%} - {risk_free_rate:.2%} = {premium:.2%}"
    }
    
    logger.success(f"✅ Market Risk Premium: {premium:.2%}")
    logger.debug(f"   Market Return: {annual_return:.2%}, Volatility: {volatility:.2%}")
    
    return result


def calculate_expected_return_capm(beta: float, 
                                   risk_free_rate: float = RISK_FREE_RATE,
                                   market_return: float = EXPECTED_MARKET_RETURN) -> float:
    """
    Calculate expected return using CAPM (convenience function).
    
    Args:
        beta: Stock beta
        risk_free_rate: Risk-free rate
        market_return: Expected market return
    
    Returns:
        Expected return
    """
    return risk_free_rate + beta * (market_return - risk_free_rate)


def comprehensive_valuation_analysis(
    stock_returns: pd.Series,
    market_returns: pd.Series,
    dividends: pd.DataFrame,
    current_price: float,
    period_name: str = "analysis period"
) -> Dict:
    """
    Perform comprehensive valuation analysis combining Beta, CAPM, and DDM.
    
    Args:
        stock_returns: Stock return series
        market_returns: Market return series
        dividends: Dividend history DataFrame
        current_price: Current stock price
        period_name: Description of the period
    
    Returns:
        Dictionary with all valuation metrics
    
    Example:
        >>> # Fetch all required data
        >>> from tools.data_tools import (fetch_stock_prices, fetch_market_index_data,
        ...                                fetch_dividends, get_aligned_returns)
        >>> 
        >>> stock_prices = fetch_stock_prices("RELIANCE", years=5)
        >>> market_prices = fetch_market_index_data(years=5)
        >>> stock_ret, market_ret = get_aligned_returns(stock_prices, market_prices)
        >>> divs = fetch_dividends("RELIANCE")
        >>> current_price = stock_prices['Close'].iloc[-1]
        >>> 
        >>> # Comprehensive analysis
        >>> analysis = comprehensive_valuation_analysis(
        ...     stock_ret, market_ret, divs, current_price, "5 years"
        ... )
        >>> 
        >>> print(f"Beta: {analysis['beta']['beta']:.2f}")
        >>> print(f"Cost of Equity: {analysis['capm']['cost_of_equity']:.2%}")
        >>> print(f"Fair Value: ₹{analysis['ddm']['fair_value']:.2f}")
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"COMPREHENSIVE VALUATION ANALYSIS - {period_name}")
    logger.info(f"{'='*60}")
    
    # 1. Calculate Beta
    beta_result = calculate_beta(stock_returns, market_returns, period_name)
    
    # 2. Calculate Cost of Equity (CAPM)
    capm_result = calculate_capm_cost_of_equity(beta_result['beta'])
    
    # 3. DDM Valuation
    ddm_result = dividend_discount_model(
        dividends,
        capm_result['cost_of_equity'],
        current_price=current_price
    )
    
    # 4. Compile results
    analysis = {
        'period': period_name,
        'current_price': current_price,
        'beta': beta_result,
        'capm': capm_result,
        'ddm': ddm_result,
        'summary': {
            'beta': beta_result['beta'],
            'beta_interpretation': beta_result['interpretation'],
            'cost_of_equity': capm_result['cost_of_equity'],
            'fair_value_ddm': ddm_result.get('fair_value'),
            'current_price': current_price,
            'recommendation': ddm_result.get('recommendation', 'N/A')
        }
    }
    
    logger.success(f"\n✅ Comprehensive valuation analysis complete!")
    logger.info(f"   Beta: {beta_result['beta']:.3f} ({beta_result['interpretation']})")
    logger.info(f"   Cost of Equity: {capm_result['cost_of_equity']:.2%}")
    if ddm_result.get('fair_value'):
        logger.info(f"   Fair Value (DDM): ₹{ddm_result['fair_value']:.2f}")
        logger.info(f"   Recommendation: {ddm_result.get('recommendation')}")
    
    return analysis


if __name__ == "__main__":
    # Test the module
    print("Testing Market Tools...")
    
    from tools.data_tools import (
        fetch_stock_prices,
        fetch_market_index_data,
        fetch_dividends,
        fetch_company_info,
        get_aligned_returns
    )
    
    test_ticker = "RELIANCE"
    
    try:
        print(f"\nFetching data for {test_ticker}...")
        
        # Fetch data
        stock_prices = fetch_stock_prices(test_ticker, years=5)
        market_prices = fetch_market_index_data(years=5)
        dividends = fetch_dividends(test_ticker)
        info = fetch_company_info(test_ticker)
        
        # Get aligned returns
        stock_ret, market_ret = get_aligned_returns(stock_prices, market_prices)
        
        # Comprehensive analysis
        analysis = comprehensive_valuation_analysis(
            stock_ret,
            market_ret,
            dividends,
            info['current_price'],
            "5 years"
        )
        
        # Display results
        print(f"\n{'='*60}")
        print("TEST RESULTS")
        print(f"{'='*60}")
        print(f"\n✅ Test successful for {test_ticker}!")
        print(f"\n📊 Risk Analysis:")
        print(f"   Beta: {analysis['beta']['beta']:.3f} ({analysis['beta']['interpretation']})")
        print(f"   Correlation with NIFTY 50: {analysis['beta']['correlation']:.3f}")
        print(f"   R-squared: {analysis['beta']['r_squared']:.3f}")
        
        print(f"\n💰 Cost of Capital:")
        print(f"   Cost of Equity (CAPM): {analysis['capm']['cost_of_equity']:.2%}")
        print(f"   Risk-Free Rate: {analysis['capm']['risk_free_rate']:.2%}")
        print(f"   Market Risk Premium: {analysis['capm']['market_risk_premium']:.2%}")
        
        if analysis['ddm'].get('fair_value'):
            print(f"\n📈 Valuation (DDM):")
            print(f"   Fair Value: ₹{analysis['ddm']['fair_value']:.2f}")
            print(f"   Current Price: ₹{analysis['current_price']:.2f}")
            print(f"   Upside/Downside: {analysis['ddm']['upside_downside']:.1%}")
            print(f"   Recommendation: {analysis['ddm']['recommendation']}")
        else:
            print(f"\n📈 Valuation (DDM): Not applicable - {analysis['ddm']['reason']}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

