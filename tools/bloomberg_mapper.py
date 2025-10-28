"""
Bloomberg Field Mapper

This module provides field name mapping between Bloomberg Terminal exports
and yfinance data structure, enabling seamless integration of Bloomberg data
into the existing workflow without modifying ratio calculators.

The mapping ensures that:
1. Bloomberg field names are converted to yfinance-compatible names
2. Existing ratio calculator code works without modification
3. Unmapped Bloomberg fields are preserved for future use
4. Critical fields are validated after mapping
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, List, Tuple, Optional, Literal
import pandas as pd
from utils.logger import logger


# ==================== FIELD MAPPINGS ====================

INCOME_STATEMENT_MAP = {
    # Revenue
    'Revenue': 'Total Revenue',
    'Sales & Services Revenue': 'Total Revenue',  # More specific, but maps to same
    'Other Revenue': 'Other Income Expense Net',
    
    # Cost of Revenue
    'Cost of Goods Sold': 'Cost Of Revenue',
    'Cost of Revenue': 'Cost Of Revenue',
    'Gross Profit': 'Gross Profit',
    
    # Operating Expenses
    'Selling, General & Admin': 'Selling General Administrative',
    'Selling General & Administrative Exp': 'Selling General Administrative',
    'Research & Development': 'Research Development',
    'Research and Development': 'Research Development',
    'Depreciation & Amortization': 'Reconciled Depreciation',
    'Other Operating Expense/(Income)': 'Other Operating Expenses',
    
    # Operating Income
    'Operating Income': 'Operating Income',
    'Operating Profit': 'Operating Income',
    'EBIT': 'EBIT',
    'EBITDA': 'EBITDA',
    
    # Non-Operating Items
    'Interest Expense': 'Interest Expense',
    'Interest Income': 'Interest Income',
    'Interest Expense, Net': 'Interest Expense Non Operating',
    'Other Non-Operating Income/(Expense)': 'Other Non Operating Income Expenses',
    
    # Pre-Tax Income
    'Pretax Income': 'Pretax Income',
    'Pre-Tax Income': 'Pretax Income',
    'Income Before Tax': 'Pretax Income',
    
    # Tax
    'Income Tax': 'Tax Provision',
    'Tax Expense': 'Tax Provision',
    'Tax Provision': 'Tax Provision',
    
    # Net Income
    'Net Income': 'Net Income',
    'Net Income to Company': 'Net Income Common Stockholders',
    'Net Income Common Stock': 'Net Income Common Stockholders',
    'Consolidated Net Income': 'Net Income',
    
    # Per Share Data
    'Diluted EPS': 'Diluted EPS',
    'Basic EPS': 'Basic EPS',
    'Diluted Normalized EPS': 'Normalized Diluted EPS',
    'Diluted EPS Excluding ExtraOrd Items': 'Diluted EPS',
    
    # Shares Outstanding
    'Diluted Shares Outstanding': 'Diluted Average Shares',
    'Basic Shares Outstanding': 'Basic Average Shares',
    'Weighted Avg Shares Outstanding': 'Diluted Average Shares',
}

BALANCE_SHEET_MAP = {
    # Assets
    'Total Assets': 'Total Assets',
    
    # Current Assets
    'Total Current Assets': 'Current Assets',
    'Current Assets': 'Current Assets',
    'Cash & Cash Equivalents': 'Cash And Cash Equivalents',
    'Cash and Cash Equivalents': 'Cash And Cash Equivalents',
    'Cash': 'Cash',
    'ST Investments': 'Other Short Term Investments',
    'Short-term Investments': 'Other Short Term Investments',
    'Accounts & Notes Receiv': 'Accounts Receivable',
    'Accounts Receivable': 'Accounts Receivable',
    'Trade Accounts Receivable': 'Accounts Receivable',
    'Inventories': 'Inventory',
    'Inventory': 'Inventory',
    'Prepaid Expenses': 'Prepaid Assets',
    'Other Current Assets': 'Other Current Assets',
    
    # Non-Current Assets
    'Total Non-Current Assets': 'Total Non Current Assets',
    'PP&E': 'Net PPE',
    'Net PP&E': 'Net PPE',
    'Property, Plant & Equipment': 'Net PPE',
    'Gross PP&E': 'Gross PPE',
    'Accumulated Depreciation': 'Accumulated Depreciation',
    'Goodwill': 'Goodwill',
    'Intangible Assets': 'Net Intangible Assets',
    'Long-term Investments': 'Long Term Investments',
    'LT Investments': 'Long Term Investments',
    'Deferred Tax Assets': 'Deferred Tax Assets Long Term',
    'Other Non-Current Assets': 'Other Non Current Assets',
    
    # Liabilities
    'Total Liabilities': 'Total Liabilities Net Minority Interest',
    
    # Current Liabilities
    'Total Current Liabilities': 'Current Liabilities',
    'Current Liabilities': 'Current Liabilities',
    'Accounts Payable': 'Accounts Payable',
    'Payables': 'Accounts Payable',
    'Trade Accounts Payable': 'Accounts Payable',
    'Short-term Debt': 'Current Debt',
    'Short Term Debt': 'Current Debt',
    'ST Debt': 'Current Debt',
    'Accrued Expenses': 'Payables And Accrued Expenses',
    'Deferred Revenue': 'Current Deferred Revenue',
    'Other Current Liabilities': 'Other Current Liabilities',
    
    # Non-Current Liabilities
    'Total Non-Current Liabilities': 'Total Non Current Liabilities Net Minority Interest',
    'Long-term Debt': 'Long Term Debt',
    'Long Term Debt': 'Long Term Debt',
    'LT Debt': 'Long Term Debt',
    'Deferred Tax Liabilities': 'Deferred Tax Liabilities Non Current',
    'Pension & Other Post-Retirement Benefit Reserves': 'Pension and Other Post Retirement Benefit Plans Current',
    'Other Non-Current Liabilities': 'Other Non Current Liabilities',
    
    # Total Debt
    'Total Debt': 'Total Debt',
    'Debt': 'Total Debt',
    
    # Equity
    'Total Equity': 'Stockholders Equity',
    'Total Shareholders\' Equity': 'Stockholders Equity',
    'Shareholders Equity': 'Stockholders Equity',
    'Common Stock': 'Common Stock',
    'Retained Earnings': 'Retained Earnings',
    'Treasury Stock': 'Treasury Stock',
    'Additional Paid-in Capital': 'Additional Paid In Capital',
    'Other Equity': 'Other Equity Adjustments',
    
    # Book Value
    'Book Value Per Share': 'Tangible Book Value',
    'Common Equity Per Share': 'Tangible Book Value',
}

CASHFLOW_MAP = {
    # Operating Activities
    'Cash from Operating Activities': 'Operating Cash Flow',
    'Operating Cash Flow': 'Operating Cash Flow',
    'Net Cash from Operations': 'Operating Cash Flow',
    'Net Income': 'Net Income From Continuing Operations',
    
    # Operating Adjustments
    'Depreciation & Amortization': 'Depreciation And Amortization',
    'Depreciation': 'Depreciation',
    'Amortization': 'Amortization',
    'Stock-Based Compensation': 'Stock Based Compensation',
    'Deferred Tax': 'Deferred Tax',
    'Change in Working Capital': 'Change In Working Capital',
    'Change in Accounts Receivable': 'Change In Accounts Receivable',
    'Change in Inventories': 'Change In Inventory',
    'Change in Accounts Payable': 'Change In Accounts Payable',
    'Other Operating Activities': 'Other Operating Cash Flow Items Total',
    
    # Investing Activities
    'Cash from Investing Activities': 'Investing Cash Flow',
    'Investing Cash Flow': 'Investing Cash Flow',
    'Net Cash from Investing': 'Investing Cash Flow',
    'Capital Expenditure': 'Capital Expenditure',
    'CapEx': 'Capital Expenditure',
    'Purchase of PP&E': 'Capital Expenditure',
    'Purchase of Fixed Assets': 'Capital Expenditure',
    'Purchase of Investments': 'Purchase Of Investment',
    'Sale of Investments': 'Sale Of Investment',
    'Acquisitions': 'Net Business Purchase And Sale',
    'Other Investing Activities': 'Net Other Investing Changes',
    
    # Financing Activities
    'Cash from Financing Activities': 'Financing Cash Flow',
    'Financing Cash Flow': 'Financing Cash Flow',
    'Net Cash from Financing': 'Financing Cash Flow',
    'Issuance of Debt': 'Issuance Of Debt',
    'Repayment of Debt': 'Repayment Of Debt',
    'Net Debt Issued': 'Net Issuance Payments Of Debt',
    'Issuance of Stock': 'Stock Issuance',
    'Repurchase of Stock': 'Repurchase Of Capital Stock',
    'Dividends Paid': 'Cash Dividends Paid',
    'Cash Dividends Paid': 'Cash Dividends Paid',
    'Dividend Payments': 'Cash Dividends Paid',
    'Other Financing Activities': 'Net Other Financing Charges',
    
    # Free Cash Flow
    'Free Cash Flow': 'Free Cash Flow',
    'FCF': 'Free Cash Flow',
    
    # Net Change
    'Net Change in Cash': 'Changes In Cash',
    'Net Cash Flow': 'Changes In Cash',
    'Beginning Cash': 'Beginning Cash Position',
    'Ending Cash': 'End Cash Position',
}

# ==================== MAPPER CLASS ====================

class BloombergFieldMapper:
    """Maps Bloomberg field names to yfinance-compatible field names."""
    
    def __init__(self):
        """Initialize the mapper with field mapping dictionaries."""
        self.income_map = INCOME_STATEMENT_MAP
        self.balance_map = BALANCE_SHEET_MAP
        self.cashflow_map = CASHFLOW_MAP
        
        logger.info("BloombergFieldMapper initialized")
        logger.info(f"  Income Statement: {len(self.income_map)} field mappings")
        logger.info(f"  Balance Sheet: {len(self.balance_map)} field mappings")
        logger.info(f"  Cash Flow: {len(self.cashflow_map)} field mappings")
    
    def map_statement(
        self,
        bloomberg_df: pd.DataFrame,
        statement_type: Literal['income', 'balance', 'cashflow']
    ) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """
        Map Bloomberg field names to yfinance-compatible names.
        
        Args:
            bloomberg_df: DataFrame from Bloomberg parser (fields as index)
            statement_type: Type of financial statement
        
        Returns:
            Tuple of (mapped_df, unmapped_fields, ambiguous_fields)
            - mapped_df: DataFrame with yfinance-compatible field names
            - unmapped_fields: Bloomberg fields that couldn't be mapped
            - ambiguous_fields: Fields that matched multiple mappings
        
        Example:
            >>> mapper = BloombergFieldMapper()
            >>> mapped_df, unmapped, ambig = mapper.map_statement(bb_df, 'income')
            >>> print(f"Mapped {len(mapped_df)} fields, {len(unmapped)} unmapped")
        """
        logger.info(f"Mapping {statement_type} statement...")
        logger.info(f"  Input: {len(bloomberg_df)} fields × {len(bloomberg_df.columns)} periods")
        
        # Select mapping dictionary
        if statement_type == 'income':
            field_map = self.income_map
        elif statement_type == 'balance':
            field_map = self.balance_map
        elif statement_type == 'cashflow':
            field_map = self.cashflow_map
        else:
            raise ValueError(f"Invalid statement_type: {statement_type}")
        
        # Perform mapping - build new index
        new_index = []
        unmapped_fields = []
        ambiguous_fields = []
        mapped_count = 0
        
        for bloomberg_field in bloomberg_df.index:
            # Clean field name (remove leading/trailing whitespace)
            clean_field = str(bloomberg_field).strip()
            
            # Check if field has direct mapping
            if clean_field in field_map:
                yfinance_field = field_map[clean_field]
                
                # Check for ambiguous mapping (multiple Bloomberg → same yfinance)
                if yfinance_field in new_index:
                    ambiguous_fields.append(clean_field)
                    logger.debug(f"  Ambiguous: '{clean_field}' → '{yfinance_field}' (already exists)")
                    # Keep original name to avoid duplicates
                    new_index.append(clean_field)
                else:
                    # Map the field
                    new_index.append(yfinance_field)
                    mapped_count += 1
                    logger.debug(f"  Mapped: '{clean_field}' → '{yfinance_field}'")
            
            else:
                # No mapping found - preserve original field name
                unmapped_fields.append(clean_field)
                new_index.append(clean_field)
                logger.debug(f"  Unmapped (preserved): '{clean_field}'")
        
        # Create mapped DataFrame by copying original and replacing index
        mapped_df = bloomberg_df.copy()
        mapped_df.index = new_index
        
        # Sort columns chronologically (oldest to newest)
        if len(mapped_df.columns) > 0:
            mapped_df = mapped_df.sort_index(axis=1)
        
        logger.success(f"✅ Mapped {statement_type} statement:")
        logger.info(f"  Output: {len(mapped_df)} fields × {len(mapped_df.columns)} periods")
        logger.info(f"  Mapped: {mapped_count} fields")
        logger.info(f"  Unmapped (preserved): {len(unmapped_fields)} fields")
        logger.info(f"  Ambiguous (skipped): {len(ambiguous_fields)} fields")
        
        if unmapped_fields:
            logger.warning(f"  Unmapped fields preserved as-is: {unmapped_fields[:5]}" + 
                          (f" ... and {len(unmapped_fields) - 5} more" if len(unmapped_fields) > 5 else ""))
        
        return mapped_df, unmapped_fields, ambiguous_fields
    
    def validate_critical_fields(
        self,
        mapped_df: pd.DataFrame,
        statement_type: Literal['income', 'balance', 'cashflow']
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate that critical fields are present after mapping.
        
        Args:
            mapped_df: Mapped DataFrame
            statement_type: Type of financial statement
        
        Returns:
            Tuple of (is_valid, missing_fields, present_fields)
        
        Example:
            >>> is_valid, missing, present = mapper.validate_critical_fields(df, 'income')
            >>> if not is_valid:
            ...     logger.warning(f"Missing critical fields: {missing}")
        """
        # Define critical fields for each statement type
        critical_fields = {
            'income': [
                'Total Revenue', 'Cost Of Revenue', 'Gross Profit',
                'Operating Income', 'Pretax Income', 'Net Income'
            ],
            'balance': [
                'Total Assets', 'Current Assets', 'Current Liabilities',
                'Total Liabilities Net Minority Interest', 'Stockholders Equity'
            ],
            'cashflow': [
                'Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow'
            ]
        }
        
        required = critical_fields.get(statement_type, [])
        present = [field for field in required if field in mapped_df.index]
        missing = [field for field in required if field not in mapped_df.index]
        
        is_valid = len(missing) == 0
        
        if is_valid:
            logger.success(f"✅ All {len(required)} critical fields present")
        else:
            logger.warning(f"⚠️  {len(missing)}/{len(required)} critical fields missing: {missing}")
        
        return is_valid, missing, present


def merge_bloomberg_yfinance(
    bloomberg_df: pd.DataFrame,
    yfinance_df: pd.DataFrame,
    primary: Literal['bloomberg', 'yfinance'] = 'bloomberg'
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Merge Bloomberg and yfinance data with primary source taking precedence.
    
    This function enables hybrid mode where Bloomberg provides historical depth
    and yfinance provides real-time updates or fills gaps.
    
    Args:
        bloomberg_df: Mapped Bloomberg DataFrame (fields as index)
        yfinance_df: Original yfinance DataFrame (fields as index)
        primary: Which source takes precedence for overlapping fields
    
    Returns:
        Tuple of (merged_df, fallback_fields)
        - merged_df: Merged DataFrame
        - fallback_fields: List of fields that used fallback source
    
    Example:
        >>> # Bloomberg is primary, yfinance fills gaps
        >>> merged, fallbacks = merge_bloomberg_yfinance(bb_df, yf_df, primary='bloomberg')
        >>> print(f"Used {len(fallbacks)} fields from yfinance fallback")
    """
    logger.info(f"Merging Bloomberg and yfinance data (primary: {primary})...")
    
    fallback_fields = []
    
    if primary == 'bloomberg':
        # Start with Bloomberg data
        merged_df = bloomberg_df.copy()
        
        # Add missing fields from yfinance
        for field in yfinance_df.index:
            if field not in merged_df.index:
                merged_df.loc[field] = yfinance_df.loc[field]
                fallback_fields.append(field)
                logger.debug(f"  Added from yfinance: {field}")
    
    else:  # primary == 'yfinance'
        # Start with yfinance data
        merged_df = yfinance_df.copy()
        
        # Add missing fields from Bloomberg
        for field in bloomberg_df.index:
            if field not in merged_df.index:
                merged_df.loc[field] = bloomberg_df.loc[field]
                fallback_fields.append(field)
                logger.debug(f"  Added from Bloomberg: {field}")
    
    logger.success(f"✅ Merged data:")
    logger.info(f"  Total fields: {len(merged_df)}")
    logger.info(f"  From primary source: {len(merged_df) - len(fallback_fields)}")
    logger.info(f"  From fallback source: {len(fallback_fields)}")
    
    return merged_df, fallback_fields


# ==================== CONVENIENCE FUNCTIONS ====================

def map_bloomberg_to_yfinance(
    bloomberg_data: Dict[str, pd.DataFrame]
) -> Dict[str, pd.DataFrame]:
    """
    Map all Bloomberg financial statements to yfinance-compatible format.
    
    This is the main entry point for Bloomberg data integration.
    
    Args:
        bloomberg_data: Dictionary with keys 'income_statement', 'balance_sheet', 'cash_flow'
    
    Returns:
        Dictionary with same keys but mapped DataFrames
    
    Example:
        >>> from tools.bloomberg_parser import parse_bloomberg_file
        >>> bb_data = parse_bloomberg_file('Tata Steel Ltd-FS,DVD,Price.xlsx')
        >>> mapped_data = map_bloomberg_to_yfinance(bb_data['data'])
        >>> # Now compatible with existing ratio calculator
    """
    logger.info("=" * 70)
    logger.info("MAPPING BLOOMBERG DATA TO YFINANCE FORMAT")
    logger.info("=" * 70)
    
    mapper = BloombergFieldMapper()
    mapped_statements = {}
    
    # Map each statement
    statement_types = {
        'income_statement': 'income',
        'balance_sheet': 'balance',
        'cash_flow': 'cashflow'
    }
    
    for key, stmt_type in statement_types.items():
        if key in bloomberg_data:
            logger.info(f"\n📊 Mapping {key.replace('_', ' ').title()}...")
            
            # Map the statement
            mapped_df, unmapped, ambiguous = mapper.map_statement(
                bloomberg_data[key],
                stmt_type
            )
            
            # Validate critical fields
            is_valid, missing, present = mapper.validate_critical_fields(
                mapped_df,
                stmt_type
            )
            
            if not is_valid:
                logger.warning(f"⚠️  Some critical fields missing in {key}, but continuing...")
            
            mapped_statements[key] = mapped_df
        else:
            logger.warning(f"⚠️  {key} not found in Bloomberg data")
    
    logger.info("\n" + "=" * 70)
    logger.success(f"✅ BLOOMBERG MAPPING COMPLETE: {len(mapped_statements)}/3 statements")
    logger.info("=" * 70 + "\n")
    
    return mapped_statements


if __name__ == "__main__":
    """Test the mapper with sample Bloomberg data."""
    from tools.bloomberg_parser import parse_bloomberg_file
    
    print("=" * 70)
    print("BLOOMBERG FIELD MAPPER TEST")
    print("=" * 70)
    
    # Find Bloomberg file
    file_path = Path.home() / 'Downloads' / 'Tata Steel Ltd-FS,DVD,Price.xlsx'
    
    if not file_path.exists():
        print(f"\n❌ Bloomberg file not found: {file_path}")
        print("Please provide path to Bloomberg Excel file as argument")
        sys.exit(1)
    
    print(f"\n📁 Using file: {file_path.name}")
    
    # Parse Bloomberg file
    print("\n📊 Step 1: Parsing Bloomberg file...")
    bloomberg_data = parse_bloomberg_file(str(file_path))
    
    # Map to yfinance format
    print("\n🔄 Step 2: Mapping to yfinance format...")
    mapped_data = map_bloomberg_to_yfinance(bloomberg_data['data'])
    
    # Display results
    print("\n" + "=" * 70)
    print("MAPPING RESULTS")
    print("=" * 70)
    
    for key, df in mapped_data.items():
        print(f"\n{key.upper().replace('_', ' ')}:")
        print(f"  Shape: {df.shape[0]} fields × {df.shape[1]} periods")
        print(f"  Periods: {list(df.columns[:2])} ... {list(df.columns[-1:])}")
        print(f"  Sample fields (first 10):")
        for field in list(df.index[:10]):
            print(f"    - {field}")
    
    print("\n✅ Mapper test complete!")

