"""
Financial Ratio Calculator for Equity Research Analysis.

This module calculates various financial ratios from company financial statements:
- Liquidity Ratios
- Efficiency Ratios  
- Solvency/Leverage Ratios
- Profitability Ratios

All ratios are calculated based on standard financial analysis formulas.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import logger


class RatioCalculator:
    """
    Calculate financial ratios from financial statements.
    
    This class provides methods to calculate various financial ratios
    used in equity research analysis.
    """
    
    def __init__(self, income_statement: pd.DataFrame, balance_sheet: pd.DataFrame, 
                 cash_flow: pd.DataFrame = None):
        """
        Initialize ratio calculator with financial statements.
        
        Args:
            income_statement: Income statement DataFrame (columns = periods)
            balance_sheet: Balance sheet DataFrame (columns = periods)
            cash_flow: Cash flow statement DataFrame (optional)
        """
        self.income_stmt = income_statement
        self.balance_sheet = balance_sheet
        self.cash_flow = cash_flow if cash_flow is not None else pd.DataFrame()
        
        # Common field name variations in yfinance data
        self.field_mappings = self._create_field_mappings()
        
        logger.info("RatioCalculator initialized")
    
    def _create_field_mappings(self) -> Dict[str, List[str]]:
        """Create mappings for common field name variations."""
        return {
            # Income Statement
            'revenue': ['Total Revenue', 'Total Revenues', 'Revenue', 'Revenues', 'Net Sales'],
            'cogs': ['Cost Of Revenue', 'Cost of Revenue', 'COGS', 'Cost of Goods Sold'],
            'gross_profit': ['Gross Profit', 'Gross Income'],
            'operating_income': ['Operating Income', 'Operating Revenue', 'EBIT'],
            'net_income': ['Net Income', 'Net Income Common Stockholders', 'Net Income Available to Common Shareholders'],
            'ebit': ['EBIT', 'Operating Income', 'Earnings Before Interest and Taxes'],
            'ebitda': ['EBITDA', 'Normalized EBITDA'],
            'interest_expense': ['Interest Expense', 'Interest Expense Non Operating', 'Net Interest Income'],
            
            # Balance Sheet - Assets
            'total_assets': ['Total Assets', 'Total Asset'],
            'current_assets': ['Current Assets', 'Total Current Assets'],
            'cash': ['Cash And Cash Equivalents', 'Cash', 'Cash and Equivalents'],
            'inventory': ['Inventory', 'Inventories'],
            'receivables': ['Receivables', 'Accounts Receivable', 'Net Receivables'],
            
            # Balance Sheet - Liabilities
            'total_liabilities': ['Total Liabilities Net Minority Interest', 'Total Liabilities', 'Total Debt'],
            'current_liabilities': ['Current Liabilities', 'Total Current Liabilities'],
            'total_debt': ['Total Debt', 'Long Term Debt And Capital Lease Obligation', 'Long Term Debt'],
            'long_term_debt': ['Long Term Debt', 'Long Term Debt And Capital Lease Obligation'],
            'short_term_debt': ['Current Debt', 'Short Term Debt', 'Current Debt And Capital Lease Obligation'],
            
            # Balance Sheet - Equity
            'total_equity': ['Total Equity Gross Minority Interest', 'Stockholders Equity', 
                           'Total Stockholder Equity', 'Shareholders Equity', 'Total Equity'],
            'shareholders_equity': ['Stockholders Equity', 'Total Stockholder Equity', 
                                   'Shareholders Equity', 'Total Equity Gross Minority Interest'],
        }
    
    def _get_value(self, statement: pd.DataFrame, field_name: str, period: int = 0) -> Optional[float]:
        """
        Get value from financial statement, handling field name variations.
        
        Args:
            statement: Financial statement DataFrame
            field_name: Standardized field name
            period: Period index (0 = most recent)
        
        Returns:
            Field value or None if not found
        """
        if statement.empty:
            return None
        
        # Get possible field names
        possible_names = self.field_mappings.get(field_name, [field_name])
        
        # Try each possible name
        for name in possible_names:
            if name in statement.index:
                try:
                    value = statement.loc[name].iloc[period]
                    if pd.notna(value):
                        return float(value)
                except (IndexError, KeyError):
                    continue
        
        return None
    
    # ==================== LIQUIDITY RATIOS ====================
    
    def current_ratio(self, period: int = 0) -> Optional[float]:
        """
        Calculate Current Ratio = Current Assets / Current Liabilities
        
        Measures ability to pay short-term obligations.
        Good: > 1.5, Acceptable: > 1.0
        
        Args:
            period: Period index (0 = most recent)
        
        Returns:
            Current ratio or None
        """
        current_assets = self._get_value(self.balance_sheet, 'current_assets', period)
        current_liabilities = self._get_value(self.balance_sheet, 'current_liabilities', period)
        
        if current_assets and current_liabilities and current_liabilities != 0:
            ratio = current_assets / current_liabilities
            logger.debug(f"Current Ratio (Period {period}): {ratio:.2f}")
            return ratio
        return None
    
    def quick_ratio(self, period: int = 0) -> Optional[float]:
        """
        Calculate Quick Ratio = (Current Assets - Inventory) / Current Liabilities
        
        Measures ability to pay short-term obligations without selling inventory.
        Good: > 1.0, Acceptable: > 0.5
        
        Args:
            period: Period index
        
        Returns:
            Quick ratio or None
        """
        current_assets = self._get_value(self.balance_sheet, 'current_assets', period)
        inventory = self._get_value(self.balance_sheet, 'inventory', period) or 0
        current_liabilities = self._get_value(self.balance_sheet, 'current_liabilities', period)
        
        if current_assets and current_liabilities and current_liabilities != 0:
            ratio = (current_assets - inventory) / current_liabilities
            logger.debug(f"Quick Ratio (Period {period}): {ratio:.2f}")
            return ratio
        return None
    
    def cash_ratio(self, period: int = 0) -> Optional[float]:
        """
        Calculate Cash Ratio = Cash / Current Liabilities
        
        Most conservative liquidity measure.
        Good: > 0.5, Acceptable: > 0.2
        
        Args:
            period: Period index
        
        Returns:
            Cash ratio or None
        """
        cash = self._get_value(self.balance_sheet, 'cash', period)
        current_liabilities = self._get_value(self.balance_sheet, 'current_liabilities', period)
        
        if cash and current_liabilities and current_liabilities != 0:
            ratio = cash / current_liabilities
            logger.debug(f"Cash Ratio (Period {period}): {ratio:.2f}")
            return ratio
        return None
    
    # ==================== EFFICIENCY RATIOS ====================
    
    def asset_turnover(self, period: int = 0) -> Optional[float]:
        """
        Calculate Asset Turnover = Revenue / Average Total Assets
        
        Measures efficiency of using assets to generate revenue.
        Higher is better (varies by industry).
        
        Args:
            period: Period index
        
        Returns:
            Asset turnover or None
        """
        revenue = self._get_value(self.income_stmt, 'revenue', period)
        total_assets = self._get_value(self.balance_sheet, 'total_assets', period)
        
        if revenue and total_assets and total_assets != 0:
            ratio = revenue / total_assets
            logger.debug(f"Asset Turnover (Period {period}): {ratio:.2f}")
            return ratio
        return None
    
    def inventory_turnover(self, period: int = 0) -> Optional[float]:
        """
        Calculate Inventory Turnover = COGS / Average Inventory
        
        Measures how quickly inventory is sold.
        Higher is generally better.
        
        Args:
            period: Period index
        
        Returns:
            Inventory turnover or None
        """
        cogs = self._get_value(self.income_stmt, 'cogs', period)
        inventory = self._get_value(self.balance_sheet, 'inventory', period)
        
        if cogs and inventory and inventory != 0:
            ratio = cogs / inventory
            logger.debug(f"Inventory Turnover (Period {period}): {ratio:.2f}")
            return ratio
        return None
    
    def receivables_turnover(self, period: int = 0) -> Optional[float]:
        """
        Calculate Receivables Turnover = Revenue / Average Receivables
        
        Measures efficiency of collecting receivables.
        Higher is better.
        
        Args:
            period: Period index
        
        Returns:
            Receivables turnover or None
        """
        revenue = self._get_value(self.income_stmt, 'revenue', period)
        receivables = self._get_value(self.balance_sheet, 'receivables', period)
        
        if revenue and receivables and receivables != 0:
            ratio = revenue / receivables
            logger.debug(f"Receivables Turnover (Period {period}): {ratio:.2f}")
            return ratio
        return None
    
    def days_sales_outstanding(self, period: int = 0) -> Optional[float]:
        """
        Calculate DSO = 365 / Receivables Turnover
        
        Average days to collect receivables.
        Lower is better.
        
        Args:
            period: Period index
        
        Returns:
            Days sales outstanding or None
        """
        receivables_turnover_ratio = self.receivables_turnover(period)
        
        if receivables_turnover_ratio and receivables_turnover_ratio != 0:
            dso = 365 / receivables_turnover_ratio
            logger.debug(f"Days Sales Outstanding (Period {period}): {dso:.1f} days")
            return dso
        return None
    
    # ==================== SOLVENCY/LEVERAGE RATIOS ====================
    
    def debt_to_equity(self, period: int = 0) -> Optional[float]:
        """
        Calculate Debt-to-Equity = Total Debt / Total Equity
        
        Measures financial leverage.
        Lower is generally better (< 1.0 preferred, varies by industry).
        
        Args:
            period: Period index
        
        Returns:
            Debt-to-equity ratio or None
        """
        total_debt = self._get_value(self.balance_sheet, 'total_debt', period)
        if total_debt is None:
            # Try calculating from long-term + short-term debt
            long_term = self._get_value(self.balance_sheet, 'long_term_debt', period) or 0
            short_term = self._get_value(self.balance_sheet, 'short_term_debt', period) or 0
            total_debt = long_term + short_term if (long_term or short_term) else None
        
        total_equity = self._get_value(self.balance_sheet, 'total_equity', period)
        
        if total_debt and total_equity and total_equity != 0:
            ratio = total_debt / total_equity
            logger.debug(f"Debt-to-Equity (Period {period}): {ratio:.2f}")
            return ratio
        return None
    
    def debt_ratio(self, period: int = 0) -> Optional[float]:
        """
        Calculate Debt Ratio = Total Liabilities / Total Assets
        
        Measures proportion of assets financed by debt.
        Lower is better (< 0.5 preferred).
        
        Args:
            period: Period index
        
        Returns:
            Debt ratio or None
        """
        total_liabilities = self._get_value(self.balance_sheet, 'total_liabilities', period)
        total_assets = self._get_value(self.balance_sheet, 'total_assets', period)
        
        if total_liabilities and total_assets and total_assets != 0:
            ratio = total_liabilities / total_assets
            logger.debug(f"Debt Ratio (Period {period}): {ratio:.2f}")
            return ratio
        return None
    
    def interest_coverage(self, period: int = 0) -> Optional[float]:
        """
        Calculate Interest Coverage = EBIT / Interest Expense
        
        Measures ability to pay interest on debt.
        Good: > 2.5, Acceptable: > 1.5
        
        Args:
            period: Period index
        
        Returns:
            Interest coverage ratio or None
        """
        ebit = self._get_value(self.income_stmt, 'ebit', period)
        if ebit is None:
            ebit = self._get_value(self.income_stmt, 'operating_income', period)
        
        interest_expense = self._get_value(self.income_stmt, 'interest_expense', period)
        
        if ebit and interest_expense and interest_expense != 0:
            # Interest expense might be negative in data
            interest_expense = abs(interest_expense)
            ratio = ebit / interest_expense
            logger.debug(f"Interest Coverage (Period {period}): {ratio:.2f}x")
            return ratio
        return None
    
    def equity_multiplier(self, period: int = 0) -> Optional[float]:
        """
        Calculate Equity Multiplier = Total Assets / Total Equity
        
        Measures financial leverage (part of DuPont analysis).
        
        Args:
            period: Period index
        
        Returns:
            Equity multiplier or None
        """
        total_assets = self._get_value(self.balance_sheet, 'total_assets', period)
        total_equity = self._get_value(self.balance_sheet, 'total_equity', period)
        
        if total_assets and total_equity and total_equity != 0:
            ratio = total_assets / total_equity
            logger.debug(f"Equity Multiplier (Period {period}): {ratio:.2f}")
            return ratio
        return None
    
    # ==================== PROFITABILITY RATIOS ====================
    
    def gross_profit_margin(self, period: int = 0) -> Optional[float]:
        """
        Calculate Gross Profit Margin = (Revenue - COGS) / Revenue
        
        Measures profitability before operating expenses.
        Higher is better.
        
        Args:
            period: Period index
        
        Returns:
            Gross profit margin (as decimal) or None
        """
        revenue = self._get_value(self.income_stmt, 'revenue', period)
        cogs = self._get_value(self.income_stmt, 'cogs', period)
        
        if revenue and cogs and revenue != 0:
            margin = (revenue - cogs) / revenue
            logger.debug(f"Gross Profit Margin (Period {period}): {margin:.2%}")
            return margin
        
        # Try direct gross profit
        gross_profit = self._get_value(self.income_stmt, 'gross_profit', period)
        if gross_profit and revenue and revenue != 0:
            margin = gross_profit / revenue
            logger.debug(f"Gross Profit Margin (Period {period}): {margin:.2%}")
            return margin
        
        return None
    
    def operating_profit_margin(self, period: int = 0) -> Optional[float]:
        """
        Calculate Operating Profit Margin = Operating Income / Revenue
        
        Measures profitability from operations.
        Higher is better.
        
        Args:
            period: Period index
        
        Returns:
            Operating profit margin (as decimal) or None
        """
        operating_income = self._get_value(self.income_stmt, 'operating_income', period)
        revenue = self._get_value(self.income_stmt, 'revenue', period)
        
        if operating_income and revenue and revenue != 0:
            margin = operating_income / revenue
            logger.debug(f"Operating Profit Margin (Period {period}): {margin:.2%}")
            return margin
        return None
    
    def net_profit_margin(self, period: int = 0) -> Optional[float]:
        """
        Calculate Net Profit Margin = Net Income / Revenue
        
        Measures overall profitability.
        Higher is better.
        
        Args:
            period: Period index
        
        Returns:
            Net profit margin (as decimal) or None
        """
        net_income = self._get_value(self.income_stmt, 'net_income', period)
        revenue = self._get_value(self.income_stmt, 'revenue', period)
        
        if net_income and revenue and revenue != 0:
            margin = net_income / revenue
            logger.debug(f"Net Profit Margin (Period {period}): {margin:.2%}")
            return margin
        return None
    
    def return_on_assets(self, period: int = 0) -> Optional[float]:
        """
        Calculate ROA = Net Income / Total Assets
        
        Measures efficiency of using assets to generate profit.
        Higher is better.
        
        Args:
            period: Period index
        
        Returns:
            ROA (as decimal) or None
        """
        net_income = self._get_value(self.income_stmt, 'net_income', period)
        total_assets = self._get_value(self.balance_sheet, 'total_assets', period)
        
        if net_income and total_assets and total_assets != 0:
            roa = net_income / total_assets
            logger.debug(f"ROA (Period {period}): {roa:.2%}")
            return roa
        return None
    
    def return_on_equity(self, period: int = 0) -> Optional[float]:
        """
        Calculate ROE = Net Income / Shareholders' Equity
        
        Measures return generated on shareholders' investment.
        Higher is better (> 15% is good).
        
        Args:
            period: Period index
        
        Returns:
            ROE (as decimal) or None
        """
        net_income = self._get_value(self.income_stmt, 'net_income', period)
        shareholders_equity = self._get_value(self.balance_sheet, 'shareholders_equity', period)
        
        if net_income and shareholders_equity and shareholders_equity != 0:
            roe = net_income / shareholders_equity
            logger.debug(f"ROE (Period {period}): {roe:.2%}")
            return roe
        return None
    
    def return_on_invested_capital(self, period: int = 0) -> Optional[float]:
        """
        Calculate ROIC = NOPAT / Invested Capital
        where NOPAT = Operating Income * (1 - Tax Rate)
        and Invested Capital = Total Equity + Total Debt
        
        Measures return on all invested capital.
        Higher is better (> 10% is good).
        
        Args:
            period: Period index
        
        Returns:
            ROIC (as decimal) or None
        """
        operating_income = self._get_value(self.income_stmt, 'operating_income', period)
        net_income = self._get_value(self.income_stmt, 'net_income', period)
        revenue = self._get_value(self.income_stmt, 'revenue', period)
        
        # Estimate tax rate
        tax_rate = 0.25  # Default Indian corporate tax rate
        if net_income and revenue:
            # Try to estimate actual tax rate
            ebit = self._get_value(self.income_stmt, 'ebit', period) or operating_income
            if ebit and ebit != 0:
                tax_rate = max(0, 1 - (net_income / ebit))
        
        # Calculate NOPAT
        if operating_income:
            nopat = operating_income * (1 - tax_rate)
        else:
            return None
        
        # Calculate Invested Capital
        total_equity = self._get_value(self.balance_sheet, 'total_equity', period)
        total_debt = self._get_value(self.balance_sheet, 'total_debt', period) or 0
        
        if total_equity:
            invested_capital = total_equity + total_debt
            if invested_capital != 0:
                roic = nopat / invested_capital
                logger.debug(f"ROIC (Period {period}): {roic:.2%}")
                return roic
        
        return None
    
    # ==================== COMPREHENSIVE ANALYSIS ====================
    
    def calculate_all_ratios(self, period: int = 0) -> Dict[str, Optional[float]]:
        """
        Calculate all available ratios for a given period.
        
        Args:
            period: Period index (0 = most recent)
        
        Returns:
            Dictionary with all calculated ratios
        """
        logger.info(f"Calculating all ratios for period {period}")
        
        ratios = {
            # Liquidity
            'current_ratio': self.current_ratio(period),
            'quick_ratio': self.quick_ratio(period),
            'cash_ratio': self.cash_ratio(period),
            
            # Efficiency
            'asset_turnover': self.asset_turnover(period),
            'inventory_turnover': self.inventory_turnover(period),
            'receivables_turnover': self.receivables_turnover(period),
            'days_sales_outstanding': self.days_sales_outstanding(period),
            
            # Solvency/Leverage
            'debt_to_equity': self.debt_to_equity(period),
            'debt_ratio': self.debt_ratio(period),
            'interest_coverage': self.interest_coverage(period),
            'equity_multiplier': self.equity_multiplier(period),
            
            # Profitability
            'gross_profit_margin': self.gross_profit_margin(period),
            'operating_profit_margin': self.operating_profit_margin(period),
            'net_profit_margin': self.net_profit_margin(period),
            'return_on_assets': self.return_on_assets(period),
            'return_on_equity': self.return_on_equity(period),
            'return_on_invested_capital': self.return_on_invested_capital(period),
        }
        
        # Count available ratios
        available = sum(1 for v in ratios.values() if v is not None)
        total = len(ratios)
        logger.success(f"✅ Calculated {available}/{total} ratios for period {period}")
        
        return ratios
    
    def calculate_ratio_trends(self, periods: int = 3) -> pd.DataFrame:
        """
        Calculate ratios across multiple periods to show trends.
        
        Args:
            periods: Number of periods to analyze
        
        Returns:
            DataFrame with ratios as rows and periods as columns
        """
        logger.info(f"Calculating ratio trends for {periods} periods")
        
        # Limit to available periods
        available_periods = min(periods, len(self.income_stmt.columns), len(self.balance_sheet.columns))
        
        trends = {}
        for period in range(available_periods):
            ratios = self.calculate_all_ratios(period)
            trends[f'Period_{period}'] = ratios
        
        df = pd.DataFrame(trends)
        logger.success(f"✅ Created trend analysis for {available_periods} periods")
        
        return df
    
    def get_ratio_summary(self, period: int = 0) -> Dict[str, Dict]:
        """
        Get comprehensive ratio summary with categories.
        
        Args:
            period: Period index
        
        Returns:
            Categorized dictionary of ratios
        """
        ratios = self.calculate_all_ratios(period)
        
        summary = {
            'liquidity': {
                'current_ratio': ratios['current_ratio'],
                'quick_ratio': ratios['quick_ratio'],
                'cash_ratio': ratios['cash_ratio'],
            },
            'efficiency': {
                'asset_turnover': ratios['asset_turnover'],
                'inventory_turnover': ratios['inventory_turnover'],
                'receivables_turnover': ratios['receivables_turnover'],
                'days_sales_outstanding': ratios['days_sales_outstanding'],
            },
            'solvency': {
                'debt_to_equity': ratios['debt_to_equity'],
                'debt_ratio': ratios['debt_ratio'],
                'interest_coverage': ratios['interest_coverage'],
                'equity_multiplier': ratios['equity_multiplier'],
            },
            'profitability': {
                'gross_profit_margin': ratios['gross_profit_margin'],
                'operating_profit_margin': ratios['operating_profit_margin'],
                'net_profit_margin': ratios['net_profit_margin'],
                'return_on_assets': ratios['return_on_assets'],
                'return_on_equity': ratios['return_on_equity'],
                'return_on_invested_capital': ratios['return_on_invested_capital'],
            }
        }
        
        return summary


# Convenience function
def calculate_ratios(income_statement: pd.DataFrame, balance_sheet: pd.DataFrame, 
                     cash_flow: pd.DataFrame = None, periods: int = 1) -> Dict:
    """
    Calculate financial ratios from statements (convenience function).
    
    Args:
        income_statement: Income statement DataFrame
        balance_sheet: Balance sheet DataFrame
        cash_flow: Cash flow statement DataFrame (optional)
        periods: Number of periods to analyze
    
    Returns:
        Dictionary with ratios and trends
    """
    calculator = RatioCalculator(income_statement, balance_sheet, cash_flow)
    
    result = {
        'latest_period': calculator.calculate_all_ratios(0),
        'summary': calculator.get_ratio_summary(0),
    }
    
    if periods > 1:
        result['trends'] = calculator.calculate_ratio_trends(periods)
    
    return result


if __name__ == "__main__":
    # Test the module
    from tools.data_tools import fetch_financial_statements
    
    print("Testing Financial Ratio Calculator...")
    
    test_ticker = "RELIANCE"
    
    try:
        # Fetch statements
        print(f"\nFetching financial statements for {test_ticker}...")
        income, balance, cashflow = fetch_financial_statements(test_ticker, "NSE")
        
        # Calculate ratios
        print(f"\nCalculating ratios for {test_ticker}...")
        calculator = RatioCalculator(income, balance, cashflow)
        
        ratios = calculator.calculate_all_ratios(0)
        
        print(f"\n✅ Test successful! Calculated {sum(1 for v in ratios.values() if v is not None)}/{len(ratios)} ratios")
        
        # Display results
        print("\n📊 LIQUIDITY RATIOS:")
        print(f"  Current Ratio: {ratios['current_ratio']:.2f}" if ratios['current_ratio'] else "  Current Ratio: N/A")
        print(f"  Quick Ratio: {ratios['quick_ratio']:.2f}" if ratios['quick_ratio'] else "  Quick Ratio: N/A")
        print(f"  Cash Ratio: {ratios['cash_ratio']:.2f}" if ratios['cash_ratio'] else "  Cash Ratio: N/A")
        
        print("\n📊 PROFITABILITY RATIOS:")
        print(f"  Gross Margin: {ratios['gross_profit_margin']:.2%}" if ratios['gross_profit_margin'] else "  Gross Margin: N/A")
        print(f"  Net Margin: {ratios['net_profit_margin']:.2%}" if ratios['net_profit_margin'] else "  Net Margin: N/A")
        print(f"  ROE: {ratios['return_on_equity']:.2%}" if ratios['return_on_equity'] else "  ROE: N/A")
        print(f"  ROA: {ratios['return_on_assets']:.2%}" if ratios['return_on_assets'] else "  ROA: N/A")
        
        print("\n📊 SOLVENCY RATIOS:")
        print(f"  Debt-to-Equity: {ratios['debt_to_equity']:.2f}" if ratios['debt_to_equity'] else "  Debt-to-Equity: N/A")
        print(f"  Interest Coverage: {ratios['interest_coverage']:.2f}x" if ratios['interest_coverage'] else "  Interest Coverage: N/A")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

