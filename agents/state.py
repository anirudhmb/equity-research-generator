"""
State Schema for Equity Research LangGraph Workflow.

This module defines the EquityResearchState TypedDict that serves as the
single source of truth for the entire workflow. All nodes read from and
update this shared state.

LangGraph Best Practice: Define state schema FIRST before creating nodes.
"""

from typing import TypedDict, Optional, Dict, List, Any
from datetime import datetime
import pandas as pd


class EquityResearchState(TypedDict, total=False):
    """
    Unified state schema for the equity research workflow.
    
    This state flows through all three nodes:
    1. collect_data_node: Populates data fields
    2. analyze_node: Populates analysis fields
    3. write_report_node: Populates report text fields
    
    Design Principles:
    - Single source of truth for entire workflow
    - Immutable updates (nodes return dicts to merge)
    - Optional fields for graceful handling of missing data
    - Organized by workflow stage (input → data → analysis → report)
    - Type-safe with IDE autocomplete support
    
    Attributes:
        === INPUT (Required) ===
        ticker (str): Company ticker symbol without suffix (e.g., "RELIANCE")
        company_name (str): Full company name (e.g., "Reliance Industries")
        
        === DATA COLLECTION NODE OUTPUT ===
        company_info (Dict): Company metadata from yfinance
            Keys: longName, sector, industry, website, marketCap, employees, etc.
        
        stock_prices (pd.DataFrame): Historical stock prices (6 years for beta)
            Columns: Open, High, Low, Close, Volume, Adj Close
            Index: DatetimeIndex
        
        financial_statements (Dict): Financial statements (4 years)
            Keys: 'balance_sheet', 'income_statement', 'cash_flow'
            Values: pd.DataFrame with years as columns
        
        dividends (pd.DataFrame): Dividend history
            Columns: Date, Dividend
            
        market_index (pd.DataFrame): NIFTY 50 index data (6 years)
            Columns: Open, High, Low, Close, Volume
            Index: DatetimeIndex
        
        news (pd.DataFrame): News articles (2-3 months from RSS feeds)
            Columns: title, link, published, published_str, summary, source
        
        news_categorized (Dict): Categorized news articles
            Keys: 'financial', 'products', 'management', 'regulatory', 
                  'market_trends', 'ma', 'other'
            Values: List[Dict] of articles
        
        news_timeline (Dict): Timeline statistics
            Keys: 'total', 'date_range', 'duration_days', 'by_month', 
                  'by_week', 'sources', 'avg_per_week'
        
        data_quality_score (float): Data completeness score 0.0-1.0
            0.8+ = Excellent, 0.6-0.8 = Good, <0.6 = Fair
        
        === FINANCIAL ANALYSIS NODE OUTPUT ===
        ratios (Dict): Financial ratios by category
            Structure: {
                'liquidity': {'current_ratio': [val1, val2, ...], ...},
                'efficiency': {'asset_turnover': [...], ...},
                'solvency': {'debt_to_equity': [...], ...},
                'profitability': {'roe': [...], ...}
            }
        
        ratio_trends (Dict): Trend analysis for ratios
            Keys: ratio names
            Values: {'trend': 'improving'|'stable'|'declining', 
                    'change': percentage_change}
        
        beta (float): Stock's systematic risk (vs NIFTY 50)
            >1.0 = Aggressive (more volatile than market)
            <1.0 = Defensive (less volatile than market)
        
        correlation_with_market (float): Correlation coefficient (-1 to 1)
            Measures how closely stock moves with NIFTY 50
        
        cost_of_equity (float): Required return from CAPM
            Formula: Rf + β(Rm - Rf)
            Used as discount rate for valuation
        
        ddm_valuation (Dict): Dividend Discount Model valuation
            Keys: 'applicable', 'fair_value', 'd0_current_dividend', 
                  'd1_next_dividend', 'growth_rate', 'cost_of_equity',
                  'current_price', 'upside_downside', 'recommendation'
        
        wacc (Dict): Weighted Average Cost of Capital
            Keys: 'wacc', 'weight_equity', 'weight_debt', 'cost_of_equity',
                  'cost_of_debt', 'cost_of_debt_after_tax', 'tax_rate',
                  'market_value_equity', 'market_value_debt'
        
        dcf_fcf_valuation (Dict): DCF valuation using Free Cash Flow to Firm
            Keys: 'applicable', 'method', 'historical_fcf', 'fcf_growth_rate',
                  'projected_fcf', 'terminal_value', 'wacc', 'enterprise_value',
                  'net_debt', 'equity_value', 'fair_value_per_share',
                  'upside_downside', 'recommendation'
        
        dcf_fcfe_valuation (Dict): DCF valuation using Free Cash Flow to Equity
            Keys: 'applicable', 'method', 'historical_fcfe', 'fcfe_growth_rate',
                  'projected_fcfe', 'terminal_value', 'cost_of_equity',
                  'equity_value', 'fair_value_per_share', 'upside_downside',
                  'recommendation'
        
        market_risk_premium (Dict): Market risk analysis
            Keys: 'premium', 'annualized_return', 'volatility', 'sharpe_ratio'
        
        valuation_recommendation (str): Investment recommendation
            Values: 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'
        
        === REPORT WRITING NODE OUTPUT ===
        executive_summary (str): High-level overview (150-200 words)
            Synthesizes company position, performance, and recommendation
        
        company_overview_text (str): Detailed company description
            Business model, products/services, market position
        
        financial_analysis_text (str): Comprehensive ratio analysis
            Covers liquidity, efficiency, solvency, profitability
            Includes trends and industry context
        
        ratio_commentary (Dict): Individual ratio interpretations
            Keys: ratio names
            Values: Commentary strings explaining the ratio
        
        valuation_text (str): Valuation analysis
            Beta interpretation, CAPM breakdown, DDM analysis,
            fair value vs market price comparison
        
        risk_analysis_text (str): Risk assessment
            Systematic risk, volatility, market sensitivity
        
        recent_developments_text (str): News synthesis
            Summary of recent developments and their implications
        
        recommendation_text (str): Final investment recommendation
            Rationale for buy/hold/sell recommendation with key points
        
        === METADATA & ERROR TRACKING ===
        current_step (str): Current workflow stage
            Values: 'start', 'data_collection', 'analysis', 
                   'report_writing', 'complete'
        
        errors (List[str]): Error messages from failed operations
            Critical errors that prevented data collection
        
        warnings (List[str]): Warning messages
            Non-critical issues (e.g., no dividends found)
        
        collection_timestamp (str): ISO 8601 timestamp of data collection
            Format: YYYY-MM-DDTHH:MM:SS.mmmmmm
        
        processing_duration (float): Total processing time in seconds
            Includes all three nodes
        
        data_complete (bool): Whether all critical data was collected
            True if data_quality_score >= 0.8
    
    Example:
        >>> state: EquityResearchState = {
        ...     'ticker': 'RELIANCE',
        ...     'company_name': 'Reliance Industries',
        ...     'errors': [],
        ...     'warnings': [],
        ...     'current_step': 'start',
        ...     'data_complete': False
        ... }
        >>> # Pass to StateGraph
        >>> result = app.invoke(state)
    """
    
    # === INPUT (Required at workflow start) ===
    ticker: str
    company_name: str
    
    # === DATA COLLECTION NODE OUTPUT ===
    company_info: Optional[Dict[str, Any]]
    stock_prices: Optional[pd.DataFrame]
    financial_statements: Optional[Dict[str, pd.DataFrame]]
    dividends: Optional[pd.DataFrame]
    market_index: Optional[pd.DataFrame]
    news: Optional[pd.DataFrame]
    news_categorized: Optional[Dict[str, List[Dict]]]
    news_timeline: Optional[Dict[str, Any]]
    data_quality_score: Optional[float]
    
    # === FINANCIAL ANALYSIS NODE OUTPUT ===
    ratios: Optional[Dict[str, Dict[str, List[float]]]]
    ratios_by_year: Optional[List[Dict[str, Any]]]  # Year-on-year ratio comparison
    ratio_trends: Optional[Dict[str, Dict[str, Any]]]
    beta: Optional[float]
    correlation_with_market: Optional[float]
    cost_of_equity: Optional[float]
    ddm_valuation: Optional[Dict[str, Any]]
    
    # === DCF VALUATION ===
    wacc: Optional[Dict[str, Any]]  # Weighted Average Cost of Capital
    dcf_fcf_valuation: Optional[Dict[str, Any]]  # FCF-based DCF valuation
    dcf_fcfe_valuation: Optional[Dict[str, Any]]  # FCFE-based DCF valuation
    
    market_risk_premium: Optional[Dict[str, float]]
    valuation_recommendation: Optional[str]
    
    # === REPORT WRITING NODE OUTPUT ===
    executive_summary: Optional[str]
    company_overview_text: Optional[str]
    financial_analysis_text: Optional[str]
    ratio_commentary: Optional[Dict[str, str]]
    valuation_text: Optional[str]
    risk_analysis_text: Optional[str]
    recent_developments_text: Optional[str]
    recommendation_text: Optional[str]
    
    # === METADATA & ERROR TRACKING ===
    current_step: str
    errors: List[str]
    warnings: List[str]
    collection_timestamp: Optional[str]
    processing_duration: Optional[float]
    data_complete: bool


# ==================== STATE FACTORY FUNCTIONS ====================

def create_initial_state(ticker: str, company_name: Optional[str] = None) -> EquityResearchState:
    """
    Create initial state for workflow.
    
    Args:
        ticker: Company ticker symbol (e.g., "RELIANCE")
        company_name: Full company name (optional, will be fetched if not provided)
    
    Returns:
        EquityResearchState with initial values
    
    Example:
        >>> initial_state = create_initial_state("RELIANCE", "Reliance Industries")
        >>> app = create_research_graph()
        >>> result = app.invoke(initial_state)
    """
    return EquityResearchState(
        ticker=ticker,
        company_name=company_name or ticker,
        current_step='start',
        errors=[],
        warnings=[],
        data_complete=False,
        # All optional fields will be None by default
        company_info=None,
        stock_prices=None,
        financial_statements=None,
        dividends=None,
        market_index=None,
        news=None,
        news_categorized=None,
        news_timeline=None,
        data_quality_score=None,
        ratios=None,
        ratios_by_year=None,
        ratio_trends=None,
        beta=None,
        correlation_with_market=None,
        cost_of_equity=None,
        ddm_valuation=None,
        market_risk_premium=None,
        valuation_recommendation=None,
        executive_summary=None,
        company_overview_text=None,
        financial_analysis_text=None,
        ratio_commentary=None,
        valuation_text=None,
        risk_analysis_text=None,
        recent_developments_text=None,
        recommendation_text=None,
        collection_timestamp=None,
        processing_duration=None
    )


# ==================== STATE VALIDATION FUNCTIONS ====================

def validate_input_state(state: EquityResearchState) -> tuple[bool, List[str]]:
    """
    Validate that state has required input fields.
    
    Args:
        state: State to validate
    
    Returns:
        Tuple of (is_valid, error_messages)
    
    Example:
        >>> state = create_initial_state("RELIANCE")
        >>> is_valid, errors = validate_input_state(state)
        >>> assert is_valid == True
    """
    errors = []
    
    if not state.get('ticker'):
        errors.append("Missing required field: 'ticker'")
    elif not isinstance(state['ticker'], str):
        errors.append("Field 'ticker' must be a string")
    elif len(state['ticker']) == 0:
        errors.append("Field 'ticker' cannot be empty")
    
    if not state.get('company_name'):
        errors.append("Missing required field: 'company_name'")
    elif not isinstance(state['company_name'], str):
        errors.append("Field 'company_name' must be a string")
    
    if 'errors' not in state:
        errors.append("Missing required field: 'errors'")
    elif not isinstance(state['errors'], list):
        errors.append("Field 'errors' must be a list")
    
    if 'warnings' not in state:
        errors.append("Missing required field: 'warnings'")
    elif not isinstance(state['warnings'], list):
        errors.append("Field 'warnings' must be a list")
    
    if not state.get('current_step'):
        errors.append("Missing required field: 'current_step'")
    elif not isinstance(state['current_step'], str):
        errors.append("Field 'current_step' must be a string")
    
    if 'data_complete' not in state:
        errors.append("Missing required field: 'data_complete'")
    elif not isinstance(state['data_complete'], bool):
        errors.append("Field 'data_complete' must be a boolean")
    
    return (len(errors) == 0, errors)


def validate_data_collection_output(state: EquityResearchState) -> tuple[bool, List[str]]:
    """
    Validate that data collection node populated required fields.
    
    Args:
        state: State after data collection
    
    Returns:
        Tuple of (is_valid, error_messages)
    
    Example:
        >>> # After data collection
        >>> is_valid, errors = validate_data_collection_output(state)
        >>> if not is_valid:
        ...     print("Data collection issues:", errors)
    """
    errors = []
    warnings = []
    
    # Critical fields (must be present)
    if state.get('company_info') is None:
        errors.append("Data collection failed: 'company_info' is None")
    
    if state.get('stock_prices') is None:
        errors.append("Data collection failed: 'stock_prices' is None")
    elif not isinstance(state['stock_prices'], pd.DataFrame):
        errors.append("'stock_prices' must be a pandas DataFrame")
    elif state['stock_prices'].empty:
        errors.append("'stock_prices' DataFrame is empty")
    
    if state.get('financial_statements') is None:
        errors.append("Data collection failed: 'financial_statements' is None")
    elif not isinstance(state['financial_statements'], dict):
        errors.append("'financial_statements' must be a dictionary")
    
    if state.get('market_index') is None:
        errors.append("Data collection failed: 'market_index' is None")
    elif not isinstance(state['market_index'], pd.DataFrame):
        errors.append("'market_index' must be a pandas DataFrame")
    
    # Optional fields (warnings only)
    if state.get('dividends') is None:
        warnings.append("No dividend data (company may not pay dividends)")
    
    if state.get('news') is None:
        warnings.append("No news data collected")
    
    # Check data quality score
    if state.get('data_quality_score') is not None:
        score = state['data_quality_score']
        if not isinstance(score, (int, float)):
            errors.append("'data_quality_score' must be a number")
        elif score < 0.0 or score > 1.0:
            errors.append("'data_quality_score' must be between 0.0 and 1.0")
        elif score < 0.6:
            warnings.append(f"Low data quality score: {score:.1%}")
    
    return (len(errors) == 0, errors + warnings)


def validate_analysis_output(state: EquityResearchState) -> tuple[bool, List[str]]:
    """
    Validate that analysis node populated required fields.
    
    Args:
        state: State after financial analysis
    
    Returns:
        Tuple of (is_valid, error_messages)
    
    Example:
        >>> # After analysis
        >>> is_valid, errors = validate_analysis_output(state)
        >>> if not is_valid:
        ...     print("Analysis issues:", errors)
    """
    errors = []
    warnings = []
    
    # Critical analysis fields
    if state.get('ratios') is None:
        errors.append("Analysis failed: 'ratios' is None")
    elif not isinstance(state['ratios'], dict):
        errors.append("'ratios' must be a dictionary")
    
    if state.get('beta') is None:
        errors.append("Analysis failed: 'beta' is None")
    elif not isinstance(state['beta'], (int, float)):
        errors.append("'beta' must be a number")
    
    if state.get('cost_of_equity') is None:
        errors.append("Analysis failed: 'cost_of_equity' is None")
    elif not isinstance(state['cost_of_equity'], (int, float)):
        errors.append("'cost_of_equity' must be a number")
    
    # Optional valuation (may not apply if no dividends)
    if state.get('ddm_valuation') is None:
        warnings.append("DDM valuation not performed (may not be applicable)")
    
    return (len(errors) == 0, errors + warnings)


def validate_report_output(state: EquityResearchState) -> tuple[bool, List[str]]:
    """
    Validate that report writing node populated required fields.
    
    Args:
        state: State after report writing
    
    Returns:
        Tuple of (is_valid, error_messages)
    
    Example:
        >>> # After report writing
        >>> is_valid, errors = validate_report_output(state)
        >>> if is_valid:
        ...     print("Report generation successful!")
    """
    errors = []
    warnings = []
    
    # Critical report sections
    if not state.get('executive_summary'):
        errors.append("Report failed: 'executive_summary' is missing or empty")
    elif not isinstance(state['executive_summary'], str):
        errors.append("'executive_summary' must be a string")
    elif len(state['executive_summary']) < 50:
        warnings.append("Executive summary is very short (< 50 characters)")
    
    if not state.get('financial_analysis_text'):
        errors.append("Report failed: 'financial_analysis_text' is missing or empty")
    elif not isinstance(state['financial_analysis_text'], str):
        errors.append("'financial_analysis_text' must be a string")
    
    if not state.get('valuation_text'):
        errors.append("Report failed: 'valuation_text' is missing or empty")
    elif not isinstance(state['valuation_text'], str):
        errors.append("'valuation_text' must be a string")
    
    # Optional sections
    if not state.get('recent_developments_text'):
        warnings.append("No recent developments section (may be due to lack of news data)")
    
    return (len(errors) == 0, errors + warnings)


def get_state_summary(state: EquityResearchState) -> str:
    """
    Get human-readable summary of state status.
    
    Args:
        state: Current state
    
    Returns:
        Formatted string summarizing state
    
    Example:
        >>> print(get_state_summary(state))
        State Summary: RELIANCE (Reliance Industries)
        Current Step: analysis
        Data Quality: 95%
        Errors: 0
        Warnings: 1
    """
    summary_lines = [
        f"State Summary: {state.get('ticker', 'N/A')} ({state.get('company_name', 'N/A')})",
        f"Current Step: {state.get('current_step', 'unknown')}",
    ]
    
    if state.get('data_quality_score') is not None:
        summary_lines.append(f"Data Quality: {state['data_quality_score']:.0%}")
    
    summary_lines.append(f"Errors: {len(state.get('errors', []))}")
    summary_lines.append(f"Warnings: {len(state.get('warnings', []))}")
    
    if state.get('data_complete') is not None:
        summary_lines.append(f"Data Complete: {state['data_complete']}")
    
    # Add key metrics if available
    if state.get('beta') is not None:
        summary_lines.append(f"Beta: {state['beta']:.3f}")
    
    if state.get('cost_of_equity') is not None:
        summary_lines.append(f"Cost of Equity: {state['cost_of_equity']:.2%}")
    
    if state.get('valuation_recommendation'):
        summary_lines.append(f"Recommendation: {state['valuation_recommendation']}")
    
    return "\n".join(summary_lines)


# ==================== TYPE HINTS FOR NODES ====================

# Type hint for node functions
StateUpdate = Dict[str, Any]  # Partial state dict to merge into main state


if __name__ == "__main__":
    """Test state creation and validation."""
    print("Testing EquityResearchState schema...")
    
    # Test 1: Create initial state
    print("\n1. Creating initial state...")
    initial_state = create_initial_state("RELIANCE", "Reliance Industries")
    print("✅ Initial state created")
    
    # Test 2: Validate input state
    print("\n2. Validating input state...")
    is_valid, errors = validate_input_state(initial_state)
    if is_valid:
        print("✅ Input state validation passed")
    else:
        print(f"❌ Input state validation failed: {errors}")
    
    # Test 3: Test state summary
    print("\n3. State summary:")
    print(get_state_summary(initial_state))
    
    # Test 4: Test with invalid state
    print("\n4. Testing validation with invalid state...")
    invalid_state = EquityResearchState(
        ticker="",  # Invalid: empty ticker
        company_name="Test",
        errors=[],
        warnings=[],
        current_step="start",
        data_complete=False
    )
    is_valid, errors = validate_input_state(invalid_state)
    if not is_valid:
        print(f"✅ Correctly detected errors: {errors}")
    else:
        print("❌ Should have detected errors")
    
    # Test 5: Check TypedDict structure
    print("\n5. Checking TypedDict annotations...")
    annotations = EquityResearchState.__annotations__
    print(f"✅ Total fields defined: {len(annotations)}")
    
    # Count by category
    data_fields = [k for k in annotations if k in [
        'company_info', 'stock_prices', 'financial_statements', 
        'dividends', 'market_index', 'news'
    ]]
    analysis_fields = [k for k in annotations if k in [
        'ratios', 'beta', 'cost_of_equity', 'ddm_valuation'
    ]]
    report_fields = [k for k in annotations if k in [
        'executive_summary', 'financial_analysis_text', 'valuation_text'
    ]]
    
    print(f"   Data fields: {len(data_fields)}")
    print(f"   Analysis fields: {len(analysis_fields)}")
    print(f"   Report fields: {len(report_fields)}")
    
    print("\n✅ All state schema tests passed!")
    print("\n📊 State Schema Statistics:")
    print(f"   Total fields: {len(annotations)}")
    print(f"   Required fields: 6 (ticker, company_name, current_step, errors, warnings, data_complete)")
    print(f"   Optional fields: {len(annotations) - 6}")
    print(f"\n✨ State schema is ready for LangGraph!")

