"""
Financial Analysis Node for Equity Research Workflow.

This node performs comprehensive financial analysis on collected data:
- 18 Financial Ratios (Liquidity, Efficiency, Solvency, Profitability)
- Beta calculation (vs NIFTY 50)
- CAPM Cost of Equity
- Dividend Discount Model (DDM) valuation
- Market Risk Premium analysis
- Valuation recommendation

The node is deterministic - no LLM reasoning needed, just mathematical
calculations using the tools we've built.
"""

import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.state import EquityResearchState
from utils.logger import logger
from config.settings import RISK_FREE_RATE, EXPECTED_MARKET_RETURN

# Import analysis tools
from tools.ratio_calculator import RatioCalculator
from tools.market_tools import (
    calculate_beta,
    calculate_capm_cost_of_equity,
    dividend_discount_model,
    calculate_market_risk_premium,
    comprehensive_valuation_analysis
)


def analyze_node(state: EquityResearchState) -> Dict[str, Any]:
    """
    Financial Analysis Node - Perform comprehensive financial analysis.
    
    This is a deterministic node that performs:
    1. Financial ratio analysis (18 ratios across 4 categories)
    2. Beta calculation (stock vs NIFTY 50)
    3. CAPM cost of equity calculation
    4. Dividend Discount Model (DDM) valuation
    5. Market risk premium analysis
    6. Final valuation recommendation
    
    The node requires data from collect_data_node and handles missing
    data gracefully, continuing with available information.
    
    Args:
        state: Current EquityResearchState with collected data
    
    Returns:
        Dict with state updates to merge into shared state:
        - ratios: Dict with calculated ratios by category
        - ratio_trends: Dict with trend analysis
        - beta: Float beta coefficient
        - correlation_with_market: Float correlation
        - cost_of_equity: Float CAPM cost of equity
        - ddm_valuation: Dict with DDM results
        - market_risk_premium: Float market risk premium
        - valuation_recommendation: String recommendation
        - current_step: Updated to 'analysis'
        - errors: List of error messages
        - warnings: List of warning messages
        - analysis_timestamp: ISO timestamp
    
    Example:
        >>> state = {collected data from data collection node}
        >>> updates = analyze_node(state)
        >>> print(f"Beta: {updates['beta']:.2f}")
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"📈 FINANCIAL ANALYSIS NODE: {state['company_name']} ({state['ticker']})")
    logger.info(f"{'='*70}\n")
    
    # Initialize state updates
    updates: Dict[str, Any] = {
        'current_step': 'analysis',
        'errors': list(state.get('errors', [])),
        'warnings': list(state.get('warnings', [])),
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    ticker = state['ticker']
    company_name = state.get('company_name', ticker)
    
    # Check if we have required data
    if not state.get('data_complete', False):
        error_msg = "Data collection incomplete - cannot perform analysis"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        return updates
    
    # Track start time
    start_time = datetime.now()
    
    # Extract data from state
    financial_statements = state.get('financial_statements', {})
    stock_prices = state.get('stock_prices')
    market_index = state.get('market_index')
    dividends = state.get('dividends')
    company_info = state.get('company_info', {})
    
    # Get current price
    current_price = None
    if stock_prices is not None and not stock_prices.empty:
        current_price = stock_prices['Close'].iloc[-1]
    elif 'current_price' in company_info:
        current_price = company_info['current_price']
    
    # ==================== 1. FINANCIAL RATIOS ====================
    logger.info("📊 Step 1/5: Calculating financial ratios...")
    try:
        balance_sheet = financial_statements.get('balance_sheet')
        income_statement = financial_statements.get('income_statement')
        cash_flow = financial_statements.get('cash_flow')
        
        if (balance_sheet is None or balance_sheet.empty or
            income_statement is None or income_statement.empty or
            cash_flow is None or cash_flow.empty):
            error_msg = "Insufficient financial statements for ratio calculation"
            updates['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
        else:
            # Initialize ratio calculator
            calculator = RatioCalculator(balance_sheet, income_statement, cash_flow)
            
            # Calculate all ratios (for most recent period)
            all_ratios = calculator.calculate_all_ratios(period=0)
            
            # Get trend analysis (across multiple periods)
            try:
                trends_df = calculator.calculate_ratio_trends(periods=3)
                # Convert to dict format for easier storage
                trends = trends_df.to_dict()
            except Exception as e:
                logger.warning(f"Could not calculate trends: {e}")
                trends = {}
            
            # Group ratios by category for easier reporting
            ratios_by_category = {
                'liquidity': {
                    'current_ratio': all_ratios.get('current_ratio'),
                    'quick_ratio': all_ratios.get('quick_ratio'),
                    'cash_ratio': all_ratios.get('cash_ratio')
                },
                'efficiency': {
                    'asset_turnover': all_ratios.get('asset_turnover'),
                    'inventory_turnover': all_ratios.get('inventory_turnover'),
                    'receivables_turnover': all_ratios.get('receivables_turnover'),
                    'days_sales_outstanding': all_ratios.get('days_sales_outstanding')
                },
                'solvency': {
                    'debt_to_equity': all_ratios.get('debt_to_equity'),
                    'debt_ratio': all_ratios.get('debt_ratio'),
                    'interest_coverage': all_ratios.get('interest_coverage'),
                    'equity_multiplier': all_ratios.get('equity_multiplier')
                },
                'profitability': {
                    'gross_profit_margin': all_ratios.get('gross_profit_margin'),
                    'operating_profit_margin': all_ratios.get('operating_profit_margin'),
                    'net_profit_margin': all_ratios.get('net_profit_margin'),
                    'return_on_assets': all_ratios.get('return_on_assets'),
                    'return_on_equity': all_ratios.get('return_on_equity'),
                    'return_on_invested_capital': all_ratios.get('return_on_invested_capital')
                }
            }
            
            updates['ratios'] = ratios_by_category
            updates['ratio_trends'] = trends
            
            logger.success("✅ Financial ratios calculated successfully!")
            
            # Count ratios by category
            for category, ratios_dict in ratios_by_category.items():
                available = sum(1 for v in ratios_dict.values() if v is not None)
                logger.info(f"   {category.capitalize()}: {available}/{len(ratios_dict)} ratios")
            
            # Show a sample ratio
            if all_ratios.get('current_ratio') is not None:
                logger.info(f"   Sample - Current Ratio: {all_ratios['current_ratio']:.2f}")
            
    except Exception as e:
        error_msg = f"Ratio calculation error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
    
    # ==================== 2. BETA CALCULATION ====================
    logger.info("\n📉 Step 2/5: Calculating Beta (vs NIFTY 50)...")
    try:
        if stock_prices is None or stock_prices.empty:
            raise ValueError("No stock price data available")
        
        if market_index is None or market_index.empty:
            raise ValueError("No market index data available")
        
        # Calculate returns
        stock_returns = stock_prices['Close'].pct_change().dropna()
        market_returns = market_index['Close'].pct_change().dropna()
        
        # Align dates
        common_dates = stock_returns.index.intersection(market_returns.index)
        stock_returns_aligned = stock_returns.loc[common_dates]
        market_returns_aligned = market_returns.loc[common_dates]
        
        # Calculate beta
        beta_result = calculate_beta(stock_returns_aligned, market_returns_aligned)
        
        updates['beta'] = beta_result['beta']
        updates['correlation_with_market'] = beta_result['correlation']
        
        logger.success(f"✅ Beta calculated: {beta_result['beta']:.3f}")
        logger.info(f"   Interpretation: {beta_result.get('interpretation', 'N/A')}")
        logger.info(f"   Correlation: {beta_result['correlation']:.3f}")
        logger.info(f"   R-squared: {beta_result.get('r_squared', 0):.3f}")
        
    except Exception as e:
        error_msg = f"Beta calculation error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        updates['beta'] = None
        updates['correlation_with_market'] = None
    
    # ==================== 3. CAPM COST OF EQUITY ====================
    logger.info("\n💰 Step 3/5: Calculating Cost of Equity (CAPM)...")
    try:
        if updates.get('beta') is None:
            raise ValueError("Beta not calculated - cannot compute CAPM")
        
        # Calculate cost of equity
        cost_of_equity = calculate_capm_cost_of_equity(
            beta=updates['beta'],
            risk_free_rate=RISK_FREE_RATE,
            market_return=EXPECTED_MARKET_RETURN
        )
        
        updates['cost_of_equity'] = cost_of_equity['cost_of_equity']
        
        logger.success(f"✅ Cost of Equity (CAPM): {cost_of_equity['cost_of_equity']:.2%}")
        logger.info(f"   Risk-Free Rate: {RISK_FREE_RATE:.2%}")
        logger.info(f"   Market Return: {EXPECTED_MARKET_RETURN:.2%}")
        logger.info(f"   Beta: {updates['beta']:.3f}")
        logger.info(f"   Equity Risk Premium: {cost_of_equity.get('equity_risk_premium', 0):.2%}")
        
    except Exception as e:
        error_msg = f"CAPM calculation error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        updates['cost_of_equity'] = None
    
    # ==================== 4. MARKET RISK PREMIUM ====================
    logger.info("\n📊 Step 4/5: Calculating Market Risk Premium...")
    try:
        if market_index is None or market_index.empty:
            raise ValueError("No market index data available")
        
        market_returns = market_index['Close'].pct_change().dropna()
        
        mrp_result = calculate_market_risk_premium(
            market_returns=market_returns,
            risk_free_rate=RISK_FREE_RATE
        )
        
        # Extract the premium value (check both possible keys)
        mrp_value = mrp_result.get('market_risk_premium') or mrp_result.get('risk_premium')
        updates['market_risk_premium'] = mrp_value
        
        if mrp_value is not None:
            logger.success(f"✅ Market Risk Premium: {mrp_value:.2%}")
            logger.info(f"   Annualized Market Return: {mrp_result.get('annualized_return', 0):.2%}")
            logger.info(f"   Market Volatility: {mrp_result.get('volatility', 0):.2%}")
        else:
            logger.warning("⚠️  Could not extract market risk premium value")
        
    except Exception as e:
        warning_msg = f"Market risk premium warning: {str(e)}"
        updates['warnings'].append(warning_msg)
        logger.warning(f"⚠️  {warning_msg}")
        updates['market_risk_premium'] = None
    
    # ==================== 5. DDM VALUATION ====================
    logger.info("\n💎 Step 5/5: Performing DDM Valuation...")
    try:
        if updates.get('cost_of_equity') is None:
            raise ValueError("Cost of equity not calculated - cannot perform DDM")
        
        if dividends is None or dividends.empty:
            # DDM not applicable for non-dividend paying companies
            warning_msg = "DDM not applicable (company doesn't pay dividends)"
            updates['warnings'].append(warning_msg)
            logger.warning(f"⚠️  {warning_msg}")
            
            updates['ddm_valuation'] = {
                'applicable': False,
                'reason': 'Company does not pay dividends',
                'fair_value': None
            }
            updates['valuation_recommendation'] = "N/A (DDM not applicable)"
        else:
            # Perform DDM valuation
            ddm_result = dividend_discount_model(
                dividends=dividends,
                cost_of_equity=updates['cost_of_equity'],
                growth_rate=None,  # Auto-calculate from history
                current_price=current_price
            )
            
            updates['ddm_valuation'] = ddm_result
            
            if ddm_result.get('applicable', False):
                fair_value = ddm_result['fair_value']
                logger.success(f"✅ DDM Fair Value: ₹{fair_value:.2f}")
                logger.info(f"   Current Dividend (D0): ₹{ddm_result.get('d0_current_dividend', 0):.2f}")
                logger.info(f"   Next Dividend (D1): ₹{ddm_result.get('d1_next_dividend', 0):.2f}")
                logger.info(f"   Growth Rate: {ddm_result.get('growth_rate', 0):.2%}")
                logger.info(f"   Cost of Equity: {ddm_result.get('cost_of_equity', 0):.2%}")
                
                if current_price:
                    logger.info(f"   Current Price: ₹{current_price:.2f}")
                    logger.info(f"   Upside/Downside: {ddm_result.get('upside_downside', 0):.1%}")
                    
                    recommendation = ddm_result.get('recommendation', 'N/A')
                    updates['valuation_recommendation'] = recommendation
                    logger.info(f"   Recommendation: {recommendation}")
                else:
                    updates['valuation_recommendation'] = "N/A (no current price)"
            else:
                reason = ddm_result.get('reason', 'Unknown')
                warning_msg = f"DDM not applicable: {reason}"
                updates['warnings'].append(warning_msg)
                logger.warning(f"⚠️  {warning_msg}")
                updates['valuation_recommendation'] = f"N/A ({reason})"
                
    except Exception as e:
        error_msg = f"DDM valuation error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        updates['ddm_valuation'] = None
        updates['valuation_recommendation'] = "N/A (valuation error)"
    
    # ==================== 6. SUMMARY ====================
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"\n{'='*70}")
    logger.success(f"✅ FINANCIAL ANALYSIS COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Duration: {duration:.2f} seconds")
    logger.info(f"Errors: {len([e for e in updates['errors'] if e not in state.get('errors', [])])}")
    logger.info(f"Warnings: {len([w for w in updates['warnings'] if w not in state.get('warnings', [])])}")
    
    # Summary of key metrics
    logger.info(f"\n📊 Key Metrics:")
    if updates.get('beta') is not None:
        logger.info(f"   Beta: {updates['beta']:.3f}")
    if updates.get('cost_of_equity') is not None:
        logger.info(f"   Cost of Equity: {updates['cost_of_equity']:.2%}")
    if updates.get('ddm_valuation') and updates['ddm_valuation'].get('applicable'):
        logger.info(f"   Fair Value (DDM): ₹{updates['ddm_valuation']['fair_value']:.2f}")
    if updates.get('valuation_recommendation'):
        logger.info(f"   Recommendation: {updates['valuation_recommendation']}")
    
    if updates['errors']:
        logger.warning(f"\n⚠️  New errors encountered:")
        for error in updates['errors']:
            if error not in state.get('errors', []):
                logger.warning(f"   - {error}")
    
    if updates['warnings']:
        new_warnings = [w for w in updates['warnings'] if w not in state.get('warnings', [])]
        if new_warnings:
            logger.info(f"\n📝 New warnings:")
            for warning in new_warnings[:5]:
                logger.info(f"   - {warning}")
    
    return updates


if __name__ == "__main__":
    """Test the financial analysis node."""
    print("Testing Financial Analysis Node...")
    
    # Import required modules
    from agents.state import create_initial_state
    from agents.nodes import collect_data_node
    
    test_ticker = "RELIANCE"
    test_company = "Reliance Industries"
    
    try:
        print(f"\n🧪 Testing with {test_ticker}...")
        
        # Step 1: Collect data
        print("\n📊 Step 1: Collecting data...")
        initial_state = create_initial_state(test_ticker, test_company)
        data_updates = collect_data_node(initial_state)
        
        # Merge updates into state
        test_state = {**initial_state, **data_updates}
        print(f"✓ Data collection: Quality {data_updates.get('data_quality_score', 0):.1%}")
        
        # Step 2: Run analysis
        print("\n📈 Step 2: Running financial analysis...")
        analysis_updates = analyze_node(test_state)
        
        # Merge analysis updates
        final_state = {**test_state, **analysis_updates}
        print("\n✓ Analysis executed")
        
        # Validate results
        print(f"\n📊 Results:")
        print(f"   Beta: {analysis_updates.get('beta', 'N/A')}")
        print(f"   Cost of Equity: {analysis_updates.get('cost_of_equity', 'N/A'):.2%}" if analysis_updates.get('cost_of_equity') else "   Cost of Equity: N/A")
        print(f"   Recommendation: {analysis_updates.get('valuation_recommendation', 'N/A')}")
        print(f"   Errors: {len([e for e in analysis_updates.get('errors', []) if e not in data_updates.get('errors', [])])}")
        print(f"   Warnings: {len([w for w in analysis_updates.get('warnings', []) if w not in data_updates.get('warnings', [])])}")
        
        # Check critical fields
        critical_fields = ['ratios', 'beta', 'cost_of_equity']
        all_present = all(analysis_updates.get(field) is not None for field in critical_fields)
        
        if all_present:
            print(f"\n✅ All critical analysis completed!")
        else:
            print(f"\n⚠️  Some analysis incomplete")
            for field in critical_fields:
                status = "✓" if analysis_updates.get(field) is not None else "✗"
                print(f"   {status} {field}")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

