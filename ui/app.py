"""
Streamlit UI for Automated Equity Research Report Generator.

This web interface allows users to generate comprehensive equity research
reports by simply entering a company ticker symbol.
"""

import sys
from pathlib import Path
import streamlit as st
from datetime import datetime
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import create_research_graph, create_initial_state
from generators import generate_word_report, generate_excel_workbook
from utils.logger import logger


# Page configuration
st.set_page_config(
    page_title="Equity Research Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Equity Research Report Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Automated research reports with LangGraph & AI</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.markdown("### About")
        st.info(
            "This tool generates comprehensive equity research reports "
            "for Indian publicly traded companies (NSE/BSE)."
        )
        
        st.markdown("### Features")
        st.markdown("""
        - 📊 **Data Collection**: 6 sources
        - 📈 **Financial Analysis**: 18 ratios
        - 💰 **Valuation**: Beta, CAPM, DDM
        - 📄 **Word Report**: Professional .docx
        - 📊 **Excel Workbook**: 9 detailed sheets
        """)
        
        st.markdown("### Supported Companies")
        st.markdown("""
        - NSE-listed companies (e.g., RELIANCE, TCS, INFY)
        - BSE-listed companies
        - Enter ticker **without** .NS or .BO suffix
        """)
        
        st.markdown("---")
        st.markdown("**Suggested Tickers:**")
        st.code("RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK")
    
    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎯 Generate Report")
        
        # Input form
        with st.form("report_form"):
            ticker = st.text_input(
                "Company Ticker Symbol",
                placeholder="e.g., RELIANCE",
                help="Enter the NSE/BSE ticker without suffix (.NS or .BO)"
            ).upper().strip()
            
            company_name = st.text_input(
                "Company Name (Optional)",
                placeholder="e.g., Reliance Industries",
                help="Optional: Enter full company name for better formatting"
            ).strip()
            
            col_a, col_b = st.columns(2)
            with col_a:
                generate_word = st.checkbox("Generate Word Report", value=True)
            with col_b:
                generate_excel = st.checkbox("Generate Excel Workbook", value=True)
            
            submitted = st.form_submit_button("🚀 Generate Report", use_container_width=True)
        
        # Generate report
        if submitted:
            if not ticker:
                st.error("⚠️ Please enter a ticker symbol!")
            elif not generate_word and not generate_excel:
                st.warning("⚠️ Please select at least one output format!")
            else:
                generate_report(ticker, company_name or ticker, generate_word, generate_excel)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">Built with LangChain, LangGraph & Streamlit | '
        f'© {datetime.now().year} Automated Equity Research</p>',
        unsafe_allow_html=True
    )


def generate_report(ticker: str, company_name: str, gen_word: bool, gen_excel: bool):
    """Generate equity research report."""
    
    st.markdown("---")
    st.markdown(f"## 📋 Generating Report for **{company_name}** ({ticker})")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Initialize
        status_text.text("🔧 Initializing workflow...")
        progress_bar.progress(10)
        
        initial_state = create_initial_state(ticker, company_name)
        app = create_research_graph()
        
        # Step 2: Data Collection
        status_text.text("📊 Collecting data (company info, prices, statements, news)...")
        progress_bar.progress(20)
        
        with st.spinner("Fetching data from yfinance, news sources..."):
            # Run workflow (this includes all 3 nodes)
            result = app.invoke(initial_state)
        
        progress_bar.progress(50)
        
        # Check for errors
        if result.get('errors'):
            st.error("⚠️ Errors encountered during data collection:")
            for error in result['errors']:
                st.warning(f"- {error}")
        
        # Check data quality
        quality = result.get('data_quality_score', 0)
        if quality < 0.6:
            st.warning(f"⚠️ Data quality: {quality:.1%} - Some data may be missing")
        else:
            st.success(f"✅ Data quality: {quality:.1%}")
        
        # Display key metrics
        display_key_metrics(result)
        
        # Step 3: Generate Documents
        status_text.text("📝 Generating documents...")
        progress_bar.progress(70)
        
        output_files = []
        
        # Generate Word report
        if gen_word:
            with st.spinner("Creating Word document..."):
                word_path = generate_word_report(result)
                output_files.append(("Word Report", word_path, "docx"))
                progress_bar.progress(85)
        
        # Generate Excel workbook
        if gen_excel:
            with st.spinner("Creating Excel workbook..."):
                excel_path = generate_excel_workbook(result)
                output_files.append(("Excel Workbook", excel_path, "xlsx"))
                progress_bar.progress(100)
        
        # Success!
        status_text.text("✅ Report generation complete!")
        
        st.markdown("---")
        st.success("🎉 **Report Generated Successfully!**")
        
        # Download buttons
        st.markdown("### 📥 Download Your Reports")
        
        cols = st.columns(len(output_files))
        for idx, (name, path, ext) in enumerate(output_files):
            with cols[idx]:
                with open(path, "rb") as file:
                    file_data = file.read()
                    st.download_button(
                        label=f"📄 Download {name}",
                        data=file_data,
                        file_name=Path(path).name,
                        mime=f"application/{'vnd.openxmlformats-officedocument.wordprocessingml.document' if ext == 'docx' else 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'}",
                        use_container_width=True
                    )
        
        # Display additional info
        st.markdown("---")
        st.markdown("### 📊 Report Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📄 Word Report Contents:**")
            st.markdown("""
            - Executive Summary
            - Company Overview
            - Financial Analysis (Ratios)
            - Valuation Analysis (Beta, CAPM, DDM)
            - Risk Analysis
            - Recent Developments
            - Investment Recommendation
            - Appendix (Financial Statements)
            """)
        
        with col2:
            st.markdown("**📊 Excel Workbook Sheets:**")
            st.markdown("""
            - Summary Dashboard
            - Financial Ratios
            - Income Statement
            - Balance Sheet
            - Cash Flow
            - Stock Prices
            - Dividends
            - Valuation Details
            - News & Developments
            """)
        
        # Warnings
        if result.get('warnings'):
            with st.expander("⚠️ View Warnings"):
                for warning in result['warnings']:
                    st.warning(warning)
        
    except Exception as e:
        progress_bar.progress(0)
        status_text.text("")
        st.error(f"❌ **Error generating report:** {str(e)}")
        st.exception(e)


def display_key_metrics(state: dict):
    """Display key metrics from the analysis."""
    
    st.markdown("### 📈 Key Metrics")
    
    # Get data
    company_info = state.get('company_info', {})
    stock_prices = state.get('stock_prices')
    ratios = state.get('ratios', {})
    beta = state.get('beta')
    cost_of_equity = state.get('cost_of_equity')
    ddm = state.get('ddm_valuation', {})
    recommendation = state.get('valuation_recommendation', 'N/A')
    
    # Current price
    current_price = 0
    if stock_prices is not None and not stock_prices.empty:
        current_price = stock_prices['Close'].iloc[-1]
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Current Price",
            value=f"₹{current_price:.2f}" if current_price else "N/A"
        )
        st.metric(
            label="Market Cap",
            value=f"₹{company_info.get('marketCap', 0) / 1e9:.2f}B" if company_info.get('marketCap') else "N/A"
        )
    
    with col2:
        st.metric(
            label="Beta",
            value=f"{beta:.3f}" if beta else "N/A",
            delta="Aggressive" if beta and beta > 1 else "Defensive" if beta else None
        )
        st.metric(
            label="Cost of Equity",
            value=f"{cost_of_equity:.2%}" if cost_of_equity else "N/A"
        )
    
    with col3:
        if ddm and ddm.get('applicable'):
            st.metric(
                label="Fair Value (DDM)",
                value=f"₹{ddm.get('fair_value', 0):.2f}"
            )
            st.metric(
                label="Upside/Downside",
                value=f"{ddm.get('upside_downside', 0):.1%}",
                delta=f"{ddm.get('upside_downside', 0):.1%}"
            )
        else:
            st.metric(label="Fair Value (DDM)", value="N/A")
            st.info("DDM not applicable for this company")
    
    with col4:
        # ROE
        roe = ratios.get('profitability', {}).get('return_on_equity')
        st.metric(
            label="Return on Equity",
            value=f"{roe:.2f}%" if roe else "N/A"
        )
        
        # Recommendation with color
        if 'Buy' in recommendation:
            st.success(f"**{recommendation}**")
        elif 'Sell' in recommendation:
            st.error(f"**{recommendation}**")
        else:
            st.warning(f"**{recommendation}**")
    
    # Additional details in expander
    with st.expander("📊 View More Financial Ratios"):
        if ratios:
            tab1, tab2, tab3, tab4 = st.tabs(["Liquidity", "Efficiency", "Solvency", "Profitability"])
            
            with tab1:
                display_ratio_table(ratios.get('liquidity', {}))
            with tab2:
                display_ratio_table(ratios.get('efficiency', {}))
            with tab3:
                display_ratio_table(ratios.get('solvency', {}))
            with tab4:
                display_ratio_table(ratios.get('profitability', {}))
        else:
            st.info("No ratio data available")


def display_ratio_table(ratios: dict):
    """Display ratios in a table."""
    if not ratios:
        st.info("No data available")
        return
    
    df = pd.DataFrame([
        {
            'Ratio': name.replace('_', ' ').title(),
            'Value': f"{value:.2f}%" if value and ('margin' in name or 'return' in name) else f"{value:.2f}" if value else "N/A"
        }
        for name, value in ratios.items()
    ])
    
    st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()

