"""
Report Writing Agent Node for Equity Research Workflow.

This node uses LLM (Groq/Gemini/Ollama) to synthesize insights from
collected data and analysis into human-readable text sections for
the final equity research report.

Unlike the previous two nodes, this is an LLM-powered agent that performs
reasoning and synthesis to generate compelling narratives.
"""

import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.state import EquityResearchState
from agents.graph import get_llm
from utils.logger import logger

# LangChain imports
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage


# ==================== PROMPTS ====================

SYSTEM_PROMPT = """You are an expert equity research analyst with deep knowledge of financial analysis, 
valuation, and investment research. Your task is to write clear, professional, and insightful sections 
for an equity research report based on provided data and analysis.

Guidelines:
- Write in a professional, analytical tone
- Use specific numbers and data points to support your analysis
- Provide balanced insights (both positives and negatives)
- Keep sections concise but comprehensive
- Use Indian market context (NSE/BSE, rupees, NIFTY 50)
- Cite specific financial metrics and ratios
- Make clear, data-driven recommendations"""


EXECUTIVE_SUMMARY_PROMPT = """Write a compelling executive summary (2-3 paragraphs) for this equity research report.

Company: {company_name} ({ticker})
Sector: {sector}
Industry: {industry}

Key Metrics:
- Current Price: ₹{current_price}
- Market Cap: ₹{market_cap}B
- Beta: {beta}
- Cost of Equity: {cost_of_equity}%

Valuation:
- Fair Value (DDM): ₹{fair_value}
- Upside/Downside: {upside_downside}%
- Recommendation: {recommendation}

Financial Highlights:
- ROE: {roe}%
- Debt to Equity: {debt_to_equity}
- Current Ratio: {current_ratio}

The executive summary should:
1. Introduce the company and its business
2. Highlight key financial metrics and performance
3. State the valuation and investment recommendation
4. Briefly mention key risks and opportunities

Write in a professional, concise style suitable for institutional investors."""


COMPANY_OVERVIEW_PROMPT = """Write a comprehensive company overview section (3-4 paragraphs).

Company: {company_name} ({ticker})
Sector: {sector}
Industry: {industry}
Description: {description}

Market Position:
- Market Cap: ₹{market_cap}B
- Employees: {employees}
- Website: {website}

Recent Developments:
{recent_news}

Cover:
1. Business overview and operations
2. Sector and industry context
3. Market position and competitive advantages
4. Recent developments and strategic initiatives

Write in an informative, analytical style."""


FINANCIAL_ANALYSIS_PROMPT = """Write a detailed financial analysis section (4-5 paragraphs) covering ratio analysis and trends.

Company: {company_name}

Liquidity Ratios:
{liquidity_ratios}

Efficiency Ratios:
{efficiency_ratios}

Solvency/Leverage Ratios:
{solvency_ratios}

Profitability Ratios:
{profitability_ratios}

Analyze:
1. Liquidity position and short-term solvency
2. Operational efficiency and asset utilization
3. Leverage and long-term financial stability
4. Profitability and returns to shareholders
5. Overall financial health assessment

Compare ratios to industry standards where appropriate. Highlight strengths and concerns."""


VALUATION_ANALYSIS_PROMPT = """Write a detailed valuation analysis section (3-4 paragraphs).

Company: {company_name}
Current Price: ₹{current_price}

Beta & Risk Metrics:
- Beta: {beta} ({beta_interpretation})
- Correlation with NIFTY 50: {correlation}
- Cost of Equity (CAPM): {cost_of_equity}%

DDM Valuation:
- Current Dividend (D0): ₹{current_dividend}
- Next Dividend (D1): ₹{next_dividend}
- Growth Rate: {growth_rate}%
- Fair Value: ₹{fair_value}
- Upside/Downside: {upside_downside}%

Recommendation: {recommendation}

Analyze:
1. Beta and systematic risk relative to market
2. Cost of equity and required return
3. DDM assumptions and valuation methodology
4. Fair value vs current price comparison
5. Investment recommendation with rationale

Discuss limitations of DDM for this company if applicable."""


RISK_ANALYSIS_PROMPT = """Write a risk analysis section (3-4 paragraphs) covering key investment risks.

Company: {company_name}
Sector: {sector}
Beta: {beta}

Financial Risks:
- Debt to Equity: {debt_to_equity}
- Interest Coverage: {interest_coverage}
- Current Ratio: {current_ratio}

Market Risks:
- Beta indicates {beta_interpretation} stock
- Correlation with market: {correlation}

Recent News Themes:
{news_categories}

Identify and analyze:
1. Systematic risk (market/beta risk)
2. Financial risk (leverage, liquidity)
3. Business/operational risks
4. Sector-specific risks
5. Company-specific risks from recent developments

Provide balanced assessment of risk factors."""


INVESTMENT_RECOMMENDATION_PROMPT = """Write a final investment recommendation section (2-3 paragraphs).

Company: {company_name}
Current Price: ₹{current_price}
Fair Value: ₹{fair_value}
Recommendation: {recommendation}

Key Strengths:
{strengths}

Key Concerns:
{concerns}

Provide:
1. Clear investment recommendation (Buy/Hold/Sell)
2. Target price and expected returns
3. Investment rationale based on analysis
4. Key factors to monitor going forward
5. Suitable investor profile (risk tolerance, time horizon)

Be decisive but balanced. Support recommendation with specific data points."""


# ==================== HELPER FUNCTIONS ====================

def format_ratio_dict(ratios: Dict[str, float]) -> str:
    """Format ratio dictionary into readable text."""
    if not ratios:
        return "No data available"
    
    lines = []
    for name, value in ratios.items():
        if value is not None:
            # Format ratio name (convert snake_case to Title Case)
            formatted_name = name.replace('_', ' ').title()
            
            # Format value (percentages vs regular numbers)
            if 'margin' in name or 'return' in name or 'ratio' in name.lower():
                if abs(value) < 10:  # Likely already a percentage
                    lines.append(f"- {formatted_name}: {value:.2f}%")
                else:
                    lines.append(f"- {formatted_name}: {value:.2f}")
            else:
                lines.append(f"- {formatted_name}: {value:.2f}")
    
    return "\n".join(lines) if lines else "No data available"


def format_news_summary(news_df) -> str:
    """Format news dataframe into summary text."""
    if news_df is None or news_df.empty:
        return "No recent news available"
    
    # Get 5 most recent articles
    recent = news_df.head(5)
    lines = []
    
    for _, row in recent.iterrows():
        date = row['published'].strftime('%Y-%m-%d')
        title = row['title'][:80] + "..." if len(row['title']) > 80 else row['title']
        lines.append(f"- {date}: {title}")
    
    return "\n".join(lines)


def format_news_categories(news_categorized: Dict) -> str:
    """Format news categories into summary text."""
    if not news_categorized:
        return "No categorized news available"
    
    lines = []
    for category, articles in news_categorized.items():
        if articles:
            lines.append(f"- {category.title()}: {len(articles)} articles")
    
    return "\n".join(lines) if lines else "No categorized news available"


def identify_strengths_concerns(state: EquityResearchState) -> tuple[str, str]:
    """Identify key strengths and concerns from analysis."""
    strengths = []
    concerns = []
    
    # Check ratios
    ratios = state.get('ratios', {})
    
    # Liquidity
    current_ratio = ratios.get('liquidity', {}).get('current_ratio')
    if current_ratio and current_ratio > 1.5:
        strengths.append(f"Strong liquidity (Current Ratio: {current_ratio:.2f})")
    elif current_ratio and current_ratio < 1.0:
        concerns.append(f"Weak liquidity (Current Ratio: {current_ratio:.2f})")
    
    # Profitability
    roe = ratios.get('profitability', {}).get('return_on_equity')
    if roe and roe > 15:
        strengths.append(f"High profitability (ROE: {roe:.2f}%)")
    elif roe and roe < 10:
        concerns.append(f"Low profitability (ROE: {roe:.2f}%)")
    
    # Leverage
    de_ratio = ratios.get('solvency', {}).get('debt_to_equity')
    if de_ratio and de_ratio < 1.0:
        strengths.append(f"Low leverage (D/E: {de_ratio:.2f})")
    elif de_ratio and de_ratio > 2.0:
        concerns.append(f"High leverage (D/E: {de_ratio:.2f})")
    
    # Valuation
    ddm = state.get('ddm_valuation', {})
    if ddm.get('applicable') and ddm.get('upside_downside'):
        upside = ddm['upside_downside']
        if upside > 0.20:
            strengths.append(f"Undervalued ({upside:.1%} upside)")
        elif upside < -0.20:
            concerns.append(f"Overvalued ({abs(upside):.1%} downside)")
    
    # Format
    strengths_text = "\n".join(f"- {s}" for s in strengths) if strengths else "- Pending detailed analysis"
    concerns_text = "\n".join(f"- {c}" for c in concerns) if concerns else "- Pending detailed analysis"
    
    return strengths_text, concerns_text


# ==================== MAIN NODE FUNCTION ====================

def write_report_node(state: EquityResearchState) -> Dict[str, Any]:
    """
    Report Writing Agent Node - Generate report text using LLM.
    
    This is an LLM-powered agent node that synthesizes insights from
    collected data and financial analysis into human-readable text sections.
    
    The node generates 9 text sections:
    1. Executive Summary
    2. Company Overview
    3. Corporate Strategy (from news)
    4. Industry & Competitor Analysis
    5. Financial Analysis (ratios)
    6. Valuation Analysis
    7. Risk Analysis
    8. Recent Developments
    9. Final Investment Recommendation
    
    Args:
        state: Complete EquityResearchState with data and analysis
    
    Returns:
        Dict with state updates to merge into shared state:
        - executive_summary: String
        - company_overview_text: String
        - corporate_strategy_text: String
        - industry_competitor_text: String
        - financial_analysis_text: String
        - valuation_text: String
        - risk_analysis_text: String
        - recent_developments_text: String
        - final_recommendation_text: String
        - current_step: Updated to 'complete'
        - errors: List of error messages
        - warnings: List of warning messages
        - writing_timestamp: ISO timestamp
    
    Example:
        >>> state = {complete data and analysis}
        >>> updates = write_report_node(state)
        >>> print(updates['executive_summary'])
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"✍️  REPORT WRITING AGENT NODE: {state['company_name']} ({state['ticker']})")
    logger.info(f"{'='*70}\n")
    
    # Initialize state updates
    updates: Dict[str, Any] = {
        'current_step': 'complete',
        'errors': list(state.get('errors', [])),
        'warnings': list(state.get('warnings', [])),
        'writing_timestamp': datetime.now().isoformat()
    }
    
    # Check prerequisites
    if not state.get('data_complete', False):
        error_msg = "Data collection incomplete - cannot write report"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        return updates
    
    if not state.get('beta') or not state.get('cost_of_equity'):
        error_msg = "Financial analysis incomplete - cannot write report"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        return updates
    
    # Track start time
    start_time = datetime.now()
    
    # Get LLM
    try:
        llm = get_llm()
        logger.success("✅ LLM configured and ready")
    except Exception as e:
        error_msg = f"LLM configuration error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        return updates
    
    # Extract data for prompts
    company_info = state.get('company_info', {})
    ratios = state.get('ratios', {})
    ddm = state.get('ddm_valuation', {})
    stock_prices = state.get('stock_prices')
    news = state.get('news')
    news_categorized = state.get('news_categorized', {})
    
    # Get current price
    current_price = stock_prices['Close'].iloc[-1] if stock_prices is not None and not stock_prices.empty else 0
    
    # Common variables for all prompts
    common_vars = {
        'company_name': state.get('company_name', state['ticker']),
        'ticker': state['ticker'],
        'sector': company_info.get('sector', 'N/A'),
        'industry': company_info.get('industry', 'N/A'),
        'current_price': current_price,
        'beta': state.get('beta', 0),
        'beta_interpretation': 'Aggressive' if state.get('beta', 1) > 1 else 'Defensive',
        'correlation': state.get('correlation_with_market', 0),
        'cost_of_equity': state.get('cost_of_equity', 0) * 100,  # Convert to percentage
    }
    
    # ==================== 1. EXECUTIVE SUMMARY ====================
    logger.info("📝 Step 1/6: Generating Executive Summary...")
    try:
        exec_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", EXECUTIVE_SUMMARY_PROMPT)
        ])
        
        exec_vars = {
            **common_vars,
            'market_cap': company_info.get('marketCap', 0) / 1e9,
            'fair_value': ddm.get('fair_value', 0) if ddm.get('applicable') else 'N/A',
            'upside_downside': ddm.get('upside_downside', 0) * 100 if ddm.get('applicable') else 'N/A',
            'recommendation': state.get('valuation_recommendation', 'N/A'),
            'roe': ratios.get('profitability', {}).get('return_on_equity', 'N/A'),
            'debt_to_equity': ratios.get('solvency', {}).get('debt_to_equity', 'N/A'),
            'current_ratio': ratios.get('liquidity', {}).get('current_ratio', 'N/A'),
        }
        
        chain = exec_prompt | llm
        response = chain.invoke(exec_vars)
        
        # Extract text from response
        if hasattr(response, 'content'):
            updates['executive_summary'] = response.content
        else:
            updates['executive_summary'] = str(response)
        
        logger.success(f"✅ Executive Summary generated ({len(updates['executive_summary'])} chars)")
        
    except Exception as e:
        error_msg = f"Executive summary error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        updates['executive_summary'] = "[Error generating executive summary]"
    
    # ==================== 2. COMPANY OVERVIEW ====================
    logger.info("\n📝 Step 2/6: Generating Company Overview...")
    try:
        company_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", COMPANY_OVERVIEW_PROMPT)
        ])
        
        company_vars = {
            **common_vars,
            'description': company_info.get('longBusinessSummary', 'No description available')[:500],
            'market_cap': company_info.get('marketCap', 0) / 1e9,
            'employees': company_info.get('fullTimeEmployees', 'N/A'),
            'website': company_info.get('website', 'N/A'),
            'recent_news': format_news_summary(news),
        }
        
        chain = company_prompt | llm
        response = chain.invoke(company_vars)
        
        updates['company_overview_text'] = response.content if hasattr(response, 'content') else str(response)
        logger.success(f"✅ Company Overview generated ({len(updates['company_overview_text'])} chars)")
        
    except Exception as e:
        error_msg = f"Company overview error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        updates['company_overview_text'] = "[Error generating company overview]"
    
    # ==================== 3. FINANCIAL ANALYSIS ====================
    logger.info("\n📝 Step 3/6: Generating Financial Analysis...")
    try:
        financial_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", FINANCIAL_ANALYSIS_PROMPT)
        ])
        
        financial_vars = {
            'company_name': common_vars['company_name'],
            'liquidity_ratios': format_ratio_dict(ratios.get('liquidity', {})),
            'efficiency_ratios': format_ratio_dict(ratios.get('efficiency', {})),
            'solvency_ratios': format_ratio_dict(ratios.get('solvency', {})),
            'profitability_ratios': format_ratio_dict(ratios.get('profitability', {})),
        }
        
        chain = financial_prompt | llm
        response = chain.invoke(financial_vars)
        
        updates['financial_analysis_text'] = response.content if hasattr(response, 'content') else str(response)
        logger.success(f"✅ Financial Analysis generated ({len(updates['financial_analysis_text'])} chars)")
        
    except Exception as e:
        error_msg = f"Financial analysis error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        updates['financial_analysis_text'] = "[Error generating financial analysis]"
    
    # ==================== 4. VALUATION ANALYSIS ====================
    logger.info("\n📝 Step 4/6: Generating Valuation Analysis...")
    try:
        valuation_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", VALUATION_ANALYSIS_PROMPT)
        ])
        
        valuation_vars = {
            **common_vars,
            'current_dividend': ddm.get('d0_current_dividend', 'N/A') if ddm.get('applicable') else 'N/A',
            'next_dividend': ddm.get('d1_next_dividend', 'N/A') if ddm.get('applicable') else 'N/A',
            'growth_rate': ddm.get('growth_rate', 0) * 100 if ddm.get('applicable') else 'N/A',
            'fair_value': ddm.get('fair_value', 'N/A') if ddm.get('applicable') else 'N/A',
            'upside_downside': ddm.get('upside_downside', 0) * 100 if ddm.get('applicable') else 'N/A',
            'recommendation': state.get('valuation_recommendation', 'N/A'),
        }
        
        chain = valuation_prompt | llm
        response = chain.invoke(valuation_vars)
        
        updates['valuation_text'] = response.content if hasattr(response, 'content') else str(response)
        logger.success(f"✅ Valuation Analysis generated ({len(updates['valuation_text'])} chars)")
        
    except Exception as e:
        error_msg = f"Valuation analysis error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        updates['valuation_text'] = "[Error generating valuation analysis]"
    
    # ==================== 5. RISK ANALYSIS ====================
    logger.info("\n📝 Step 5/6: Generating Risk Analysis...")
    try:
        risk_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", RISK_ANALYSIS_PROMPT)
        ])
        
        risk_vars = {
            **common_vars,
            'debt_to_equity': ratios.get('solvency', {}).get('debt_to_equity', 'N/A'),
            'interest_coverage': ratios.get('solvency', {}).get('interest_coverage', 'N/A'),
            'current_ratio': ratios.get('liquidity', {}).get('current_ratio', 'N/A'),
            'news_categories': format_news_categories(news_categorized),
        }
        
        chain = risk_prompt | llm
        response = chain.invoke(risk_vars)
        
        updates['risk_analysis_text'] = response.content if hasattr(response, 'content') else str(response)
        logger.success(f"✅ Risk Analysis generated ({len(updates['risk_analysis_text'])} chars)")
        
    except Exception as e:
        error_msg = f"Risk analysis error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        updates['risk_analysis_text'] = "[Error generating risk analysis]"
    
    # ==================== 6. FINAL RECOMMENDATION ====================
    logger.info("\n📝 Step 6/6: Generating Final Recommendation...")
    try:
        strengths, concerns = identify_strengths_concerns(state)
        
        recommendation_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", INVESTMENT_RECOMMENDATION_PROMPT)
        ])
        
        recommendation_vars = {
            'company_name': common_vars['company_name'],
            'current_price': current_price,
            'fair_value': ddm.get('fair_value', 'N/A') if ddm.get('applicable') else 'N/A',
            'recommendation': state.get('valuation_recommendation', 'N/A'),
            'strengths': strengths,
            'concerns': concerns,
        }
        
        chain = recommendation_prompt | llm
        response = chain.invoke(recommendation_vars)
        
        updates['final_recommendation_text'] = response.content if hasattr(response, 'content') else str(response)
        logger.success(f"✅ Final Recommendation generated ({len(updates['final_recommendation_text'])} chars)")
        
    except Exception as e:
        error_msg = f"Final recommendation error: {str(e)}"
        updates['errors'].append(error_msg)
        logger.error(f"❌ {error_msg}")
        updates['final_recommendation_text'] = "[Error generating final recommendation]"
    
    # ==================== 7. PLACEHOLDER SECTIONS ====================
    # These can be enhanced with more specific prompts later
    updates['corporate_strategy_text'] = "Corporate strategy analysis pending."
    updates['industry_competitor_text'] = "Industry and competitor analysis pending."
    updates['recent_developments_text'] = format_news_summary(news) if news is not None else "No recent developments available."
    
    # ==================== 8. SUMMARY ====================
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"\n{'='*70}")
    logger.success(f"✅ REPORT WRITING COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Duration: {duration:.2f} seconds")
    logger.info(f"Sections Generated: 9")
    logger.info(f"Total Characters: {sum(len(str(updates.get(k, ''))) for k in ['executive_summary', 'company_overview_text', 'financial_analysis_text', 'valuation_text', 'risk_analysis_text', 'final_recommendation_text'])}")
    logger.info(f"Errors: {len([e for e in updates['errors'] if e not in state.get('errors', [])])}")
    logger.info(f"Warnings: {len([w for w in updates['warnings'] if w not in state.get('warnings', [])])}")
    
    if updates['errors']:
        logger.warning(f"\n⚠️  New errors encountered:")
        for error in updates['errors']:
            if error not in state.get('errors', []):
                logger.warning(f"   - {error}")
    
    return updates


if __name__ == "__main__":
    """Test the report writing node (requires LLM API keys)."""
    print("Testing Report Writing Agent Node...")
    print("\n⚠️  This test requires LLM API keys (Groq/Gemini/Ollama)")
    print("     Set GROQ_API_KEY or GEMINI_API_KEY in .env file\n")
    
    # Import required modules
    from agents.state import create_initial_state
    from agents.nodes import collect_data_node, analyze_node
    
    test_ticker = "RELIANCE"
    test_company = "Reliance Industries"
    
    try:
        print(f"🧪 Testing with {test_ticker}...")
        
        # Step 1: Collect data
        print("\n📊 Step 1: Collecting data...")
        initial_state = create_initial_state(test_ticker, test_company)
        data_updates = collect_data_node(initial_state)
        test_state = {**initial_state, **data_updates}
        print(f"✓ Data quality: {data_updates.get('data_quality_score', 0):.1%}")
        
        # Step 2: Analyze
        print("\n📈 Step 2: Running analysis...")
        analysis_updates = analyze_node(test_state)
        test_state = {**test_state, **analysis_updates}
        print(f"✓ Analysis complete")
        
        # Step 3: Write report
        print("\n✍️  Step 3: Writing report with LLM...")
        writing_updates = write_report_node(test_state)
        
        print("\n📊 Results:")
        print(f"   Sections Generated: {sum(1 for k in ['executive_summary', 'company_overview_text', 'financial_analysis_text', 'valuation_text', 'risk_analysis_text', 'final_recommendation_text'] if writing_updates.get(k) and not writing_updates[k].startswith('[Error'))}")
        print(f"   Errors: {len([e for e in writing_updates.get('errors', []) if e not in analysis_updates.get('errors', [])])}")
        
        # Show sample output
        if writing_updates.get('executive_summary'):
            print(f"\n✅ Sample Output (Executive Summary):")
            print(f"{writing_updates['executive_summary'][:300]}...")
        
        print(f"\n✅ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

