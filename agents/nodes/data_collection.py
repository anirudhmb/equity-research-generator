"""
Data Collection Node for Equity Research Workflow.

This node orchestrates the collection of all data required for equity research:
- Company information from yfinance
- Historical stock prices (6 years for beta calculation)
- Financial statements (4 years due to yfinance limitations)
- Dividend history
- Market index data (NIFTY 50)
- News and recent developments (2-3 months from RSS feeds)

The node is deterministic - no LLM reasoning is needed, just data fetching
and validation in a fixed workflow.
"""

import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.state import EquityResearchState
from utils.logger import logger
from config.settings import NSE_SUFFIX, DEFAULT_MARKET_INDEX, YEARS_OF_DATA, MONTHS_OF_NEWS

# Import data collection tools
from tools.data_tools import fetch_all_company_data
from tools.news_scraper import (
    fetch_all_news,
    categorize_news,
    get_news_timeline
)


def collect_data_node(state: EquityResearchState) -> Dict[str, Any]:
    """
    Data Collection Node - Fetch all required data for equity research.
    
    This is a deterministic node that follows a fixed workflow to collect:
    1. Company information
    2. Historical stock prices (6 years)
    3. Financial statements (4 years)
    4. Dividend history
    5. Market index (NIFTY 50, 6 years)
    6. News and developments (2-3 months)
    
    The node handles errors gracefully and continues even if some data
    sources fail, tracking errors and warnings in the state.
    
    Args:
        state: Current EquityResearchState with at least ticker and company_name
    
    Returns:
        Dict with state updates to merge into shared state:
        - company_info: Dict with company metadata
        - stock_prices: DataFrame with price history
        - financial_statements: Dict with balance sheet, income, cash flow
        - dividends: DataFrame with dividend history (or None)
        - market_index: DataFrame with NIFTY 50 data
        - news: DataFrame with news articles (or None)
        - news_categorized: Dict with categorized news
        - news_timeline: Dict with timeline statistics
        - data_quality_score: Float 0-1 indicating completeness
        - current_step: Updated to 'data_collection'
        - errors: List of error messages
        - warnings: List of warning messages
        - collection_timestamp: ISO timestamp
    
    Example:
        >>> state = create_initial_state("RELIANCE", "Reliance Industries")
        >>> updates = collect_data_node(state)
        >>> print(f"Quality: {updates['data_quality_score']:.1%}")
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"📊 DATA COLLECTION NODE: {state['company_name']} ({state['ticker']})")
    logger.info(f"{'='*70}\n")
    
    # Initialize state updates
    updates: Dict[str, Any] = {
        'current_step': 'data_collection',
        'errors': list(state.get('errors', [])),  # Copy existing errors
        'warnings': list(state.get('warnings', [])),  # Copy existing warnings
        'collection_timestamp': datetime.now().isoformat()
    }
    
    ticker = state['ticker']
    company_name = state.get('company_name', ticker)
    
    # Track start time for duration calculation
    start_time = datetime.now()
    
    # ==================== 1-5. FINANCIAL DATA (using wrapper) ====================
    logger.info("📊 Step 1/2: Fetching all financial data (info, prices, statements, dividends, market index)...")
    try:
        # Use the comprehensive wrapper function (fetches 6 years of data)
        financial_data = fetch_all_company_data(
            ticker,
            exchange="NSE",
            years=YEARS_OF_DATA + 1,  # Request 6 years
            save_to_file=False  # We'll save later in document generation
        )
        
        # Extract components
        updates['company_info'] = financial_data.get('info', {})
        updates['stock_prices'] = financial_data.get('prices', None)
        updates['market_index'] = financial_data.get('market_index', None)
        updates['dividends'] = financial_data.get('dividends', None)
        
        # Financial statements (combine into dict)
        updates['financial_statements'] = {
            'income_statement': financial_data.get('income_statement', None),
            'balance_sheet': financial_data.get('balance_sheet', None),
            'cash_flow': financial_data.get('cash_flow', None)
        }
        
        # Update company name if we got a better one
        if 'company_name' in updates['company_info']:
            updates['company_name'] = updates['company_info']['company_name']
            company_name = updates['company_name']
        
        # Log what we got
        logger.success("✅ Financial data collected successfully!")
        logger.info(f"   Company: {company_name}")
        logger.info(f"   Sector: {updates['company_info'].get('sector', 'N/A')}")
        
        if updates['stock_prices'] is not None and not updates['stock_prices'].empty:
            logger.info(f"   Stock Prices: {len(updates['stock_prices'])} trading days")
        else:
            updates['errors'].append("No stock price data available")
        
        # Check financial statements
        bs = updates['financial_statements']['balance_sheet']
        inc = updates['financial_statements']['income_statement']
        cf = updates['financial_statements']['cash_flow']
        
        if bs is not None and not bs.empty:
            logger.info(f"   Balance Sheet: {len(bs.columns)} periods")
        else:
            updates['errors'].append("No balance sheet data")
        
        if inc is not None and not inc.empty:
            logger.info(f"   Income Statement: {len(inc.columns)} periods")
        else:
            updates['errors'].append("No income statement data")
        
        if cf is not None and not cf.empty:
            logger.info(f"   Cash Flow: {len(cf.columns)} periods")
        else:
            updates['errors'].append("No cash flow data")
        
        # Dividends (optional)
        if updates['dividends'] is not None and not updates['dividends'].empty:
            logger.info(f"   Dividends: {len(updates['dividends'])} payments")
        else:
            warning_msg = "No dividend history (company may not pay dividends)"
            updates['warnings'].append(warning_msg)
            logger.warning(f"   ⚠️  {warning_msg}")
        
        # Market index
        if updates['market_index'] is not None and not updates['market_index'].empty:
            logger.info(f"   Market Index (NIFTY 50): {len(updates['market_index'])} trading days")
        else:
            updates['errors'].append("No market index data")
            
    except Exception as e:
        error_msg = f"Financial data error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
    
    # ==================== 6. NEWS & DEVELOPMENTS ====================
    logger.info("\n📰 Step 2/2: Fetching news and developments...")
    try:
        news_df = fetch_all_news(company_name, ticker, months=MONTHS_OF_NEWS)
        
        if not news_df.empty:
            updates['news'] = news_df
            
            # Categorize news
            categorized = categorize_news(news_df)
            updates['news_categorized'] = categorized
            
            # Get timeline statistics
            timeline = get_news_timeline(news_df)
            updates['news_timeline'] = timeline
            
            logger.success(f"✅ News: {len(news_df)} unique articles")
            logger.info(f"   Date Range: {timeline.get('date_range', 'N/A')}")
            logger.info(f"   Sources: {len(timeline.get('sources', {}))} different sources")
            
            # Show category breakdown
            financial_count = len(categorized.get('financial', []))
            if financial_count > 0:
                logger.info(f"   Financial News: {financial_count} articles")
        else:
            # No news is a warning, not an error
            updates['news'] = None
            updates['news_categorized'] = None
            updates['news_timeline'] = None
            warning_msg = "No news articles found (RSS feeds may have limited retention)"
            updates['warnings'].append(warning_msg)
            logger.warning(f"⚠️  {warning_msg}")
            
    except Exception as e:
        # News fetch failure is a warning
        updates['news'] = None
        updates['news_categorized'] = None
        updates['news_timeline'] = None
        warning_msg = f"News warning: {str(e)}"
        updates['warnings'].append(warning_msg)
        logger.warning(f"⚠️  {warning_msg}")
    
    # ==================== 7. CALCULATE DATA QUALITY SCORE ====================
    logger.info(f"\n🔍 Calculating data quality score...")
    
    quality_score = _calculate_data_quality(updates)
    updates['data_quality_score'] = quality_score
    
    # Determine if we have sufficient data
    updates['data_complete'] = quality_score >= 0.8
    
    # Log quality assessment
    if quality_score >= 0.9:
        logger.success(f"✅ Data quality: {quality_score:.1%} (Excellent)")
    elif quality_score >= 0.8:
        logger.success(f"✅ Data quality: {quality_score:.1%} (Good)")
    elif quality_score >= 0.6:
        logger.info(f"📊 Data quality: {quality_score:.1%} (Fair)")
    else:
        logger.warning(f"⚠️  Data quality: {quality_score:.1%} (Limited)")
    
    # ==================== 8. SUMMARY ====================
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"\n{'='*70}")
    logger.success(f"✅ DATA COLLECTION COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Duration: {duration:.2f} seconds")
    logger.info(f"Quality Score: {quality_score:.1%}")
    logger.info(f"Data Complete: {updates['data_complete']}")
    logger.info(f"Errors: {len(updates['errors'])}")
    logger.info(f"Warnings: {len(updates['warnings'])}")
    
    if updates['errors']:
        logger.warning(f"\n⚠️  Errors encountered:")
        for error in updates['errors']:
            logger.warning(f"   - {error}")
    
    if updates['warnings']:
        logger.info(f"\n📝 Warnings:")
        for warning in updates['warnings'][:5]:  # Show first 5
            logger.info(f"   - {warning}")
    
    return updates


def _calculate_data_quality(data: Dict[str, Any]) -> float:
    """
    Calculate data quality score based on what was collected.
    
    Scoring:
    - Company info: 1.0 (critical)
    - Stock prices: 1.0 (critical)
    - Financial statements: 1.5 (most critical)
    - Market index: 1.0 (critical for beta)
    - Dividends: 0.5 (optional, not all companies pay)
    - News: 0.5 (optional, RSS feeds limited)
    
    Total: 5.5 points maximum
    Score = (points_earned / 5.5)
    
    Args:
        data: Dict with collected data
    
    Returns:
        Float between 0.0 and 1.0
    """
    score = 0.0
    max_score = 5.5
    
    # Company info (1.0 points)
    if data.get('company_info'):
        score += 1.0
    
    # Stock prices (1.0 points)
    if data.get('stock_prices') is not None:
        import pandas as pd
        if isinstance(data['stock_prices'], pd.DataFrame) and not data['stock_prices'].empty:
            # Bonus for sufficient data (at least 1 year)
            if len(data['stock_prices']) >= 250:  # ~1 year of trading days
                score += 1.0
            else:
                score += 0.5
    
    # Financial statements (1.5 points - most critical)
    if data.get('financial_statements'):
        statements = data['financial_statements']
        
        # Check each statement type
        bs_ok = not statements.get('balance_sheet', pd.DataFrame()).empty
        is_ok = not statements.get('income_statement', pd.DataFrame()).empty
        cf_ok = not statements.get('cash_flow', pd.DataFrame()).empty
        
        if bs_ok and is_ok and cf_ok:
            # Check if we have sufficient periods (at least 3)
            import pandas as pd
            bs_periods = len(statements['balance_sheet'].columns) if isinstance(statements['balance_sheet'], pd.DataFrame) else 0
            is_periods = len(statements['income_statement'].columns) if isinstance(statements['income_statement'], pd.DataFrame) else 0
            cf_periods = len(statements['cash_flow'].columns) if isinstance(statements['cash_flow'], pd.DataFrame) else 0
            
            min_periods = min(bs_periods, is_periods, cf_periods)
            
            if min_periods >= 4:
                score += 1.5
            elif min_periods >= 3:
                score += 1.2
            elif min_periods >= 2:
                score += 0.8
            else:
                score += 0.4
    
    # Market index (1.0 points - needed for beta)
    if data.get('market_index') is not None:
        import pandas as pd
        if isinstance(data['market_index'], pd.DataFrame) and not data['market_index'].empty:
            if len(data['market_index']) >= 250:  # At least 1 year
                score += 1.0
            else:
                score += 0.5
    
    # Dividends (0.5 points - optional)
    if data.get('dividends') is not None:
        import pandas as pd
        if isinstance(data['dividends'], pd.DataFrame) and not data['dividends'].empty:
            score += 0.5
    else:
        # Give partial credit even if no dividends (not all companies pay)
        score += 0.25
    
    # News (0.5 points - optional)
    if data.get('news') is not None:
        import pandas as pd
        if isinstance(data['news'], pd.DataFrame) and not data['news'].empty:
            # Bonus for good coverage
            if len(data['news']) >= 50:
                score += 0.5
            elif len(data['news']) >= 20:
                score += 0.4
            else:
                score += 0.3
        else:
            score += 0.2  # Some partial credit
    else:
        score += 0.2  # Partial credit (RSS limitations are expected)
    
    # Normalize to 0-1 range
    quality = score / max_score
    
    return min(1.0, quality)  # Cap at 1.0


if __name__ == "__main__":
    """Test the data collection node."""
    print("Testing Data Collection Node...")
    
    # Import state creation
    from agents.state import create_initial_state
    
    test_ticker = "RELIANCE"
    test_company = "Reliance Industries"
    
    try:
        print(f"\n🧪 Testing with {test_ticker}...")
        
        # Create initial state
        initial_state = create_initial_state(test_ticker, test_company)
        print("✓ Initial state created")
        
        # Run data collection
        updates = collect_data_node(initial_state)
        print("\n✓ Data collection executed")
        
        # Validate results
        print(f"\n📊 Results:")
        print(f"   Quality Score: {updates.get('data_quality_score', 0):.1%}")
        print(f"   Data Complete: {updates.get('data_complete', False)}")
        print(f"   Errors: {len(updates.get('errors', []))}")
        print(f"   Warnings: {len(updates.get('warnings', []))}")
        
        # Check critical fields
        critical_fields = ['company_info', 'stock_prices', 'financial_statements', 'market_index']
        all_present = all(updates.get(field) is not None for field in critical_fields)
        
        if all_present:
            print(f"\n✅ All critical data collected!")
        else:
            print(f"\n⚠️  Some critical data missing")
            for field in critical_fields:
                status = "✓" if updates.get(field) is not None else "✗"
                print(f"   {status} {field}")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

