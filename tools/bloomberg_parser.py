"""
Bloomberg Terminal Data Parser

This module parses Bloomberg Excel exports and converts them to pandas DataFrames
compatible with our existing workflow.

Supported Bloomberg export formats:
- Financial Statements (Income, Balance Sheet, Cash Flow)
- Dividend data
- Stock prices

Author: Equity Research Generator
Created: October 23, 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# Import logger (with fallback for direct script execution)
try:
    from utils.logger import logger
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.logger import logger


class BloombergParser:
    """
    Parse Bloomberg Terminal Excel exports.
    
    Bloomberg exports typically have this structure:
    - Row 0: Company name header
    - Row 1: Empty
    - Row 2: Column labels (FY 2019, FY 2020, etc.)
    - Row 3: Dates (03/31/2019, 03/31/2020, etc.) ← Use as column headers
    - Row 4+: Data rows (Field Name | Bloomberg Code | Values...)
    """
    
    def __init__(self, file_path: str):
        """
        Initialize Bloomberg parser.
        
        Args:
            file_path: Path to Bloomberg Excel file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Bloomberg file not found: {file_path}")
        
        logger.info(f"Initializing Bloomberg parser for: {self.file_path.name}")
        
        # Load Excel file
        self.xl = pd.ExcelFile(self.file_path)
        self.sheet_names = self.xl.sheet_names
        
        logger.info(f"   Sheets found: {', '.join(self.sheet_names)}")
    
    def parse_financial_statement(self, sheet_name: str) -> pd.DataFrame:
        """
        Parse a financial statement sheet (Income, Balance Sheet, Cash Flow).
        
        Args:
            sheet_name: Name of the sheet to parse
        
        Returns:
            DataFrame with dates as columns and line items as rows
        """
        logger.info(f"Parsing sheet: {sheet_name}")
        
        # Read the sheet
        df_raw = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)
        
        # Extract company name from first row
        company_name = df_raw.iloc[0, 0]
        logger.debug(f"   Company: {company_name}")
        
        # Extract dates from row 4 (0-indexed row 4 = 5th row, has "12 Months Ending" label)
        # Row structure:
        #   Row 0: Company name
        #   Row 1: Empty
        #   Row 2: "In Millions of INR..." header
        #   Row 3: "FY 2019", "FY 2020" labels
        #   Row 4: "12 Months Ending" label | NaN | "03/31/2019" | "03/31/2020" | ...
        dates_row = df_raw.iloc[4, 2:]  # Skip first 2 columns (label and NaN)
        dates = []
        for date_val in dates_row:
            if pd.notna(date_val):
                try:
                    # Handle string dates like '03/31/2019'
                    if isinstance(date_val, str):
                        date_obj = pd.to_datetime(date_val)
                    else:
                        date_obj = pd.Timestamp(date_val)
                    dates.append(date_obj)
                except:
                    # Skip invalid dates (like "Current", "Est", etc.)
                    pass
        
        logger.debug(f"   Dates found: {len(dates)}")
        
        # Extract data rows (starting from row 5, which is 0-indexed row 5)
        # Row 5 onwards contain field name | bloomberg code | data values
        data_rows = []
        field_names = []
        
        for idx in range(5, len(df_raw)):
            row = df_raw.iloc[idx, :]
            field_name = row[0]
            
            # Skip empty rows or rows without field names
            if pd.isna(field_name) or str(field_name).strip() == '':
                continue
            
            # Get values for this field (skip first 2 columns)
            values = row[2:2+len(dates)].values
            
            # Convert to numeric
            values_numeric = []
            for val in values:
                try:
                    if pd.isna(val) or val == '—' or val == '#N/A':
                        values_numeric.append(np.nan)
                    else:
                        values_numeric.append(float(val))
                except (ValueError, TypeError):
                    values_numeric.append(np.nan)
            
            field_names.append(field_name)
            data_rows.append(values_numeric)
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, index=field_names, columns=dates)
        
        # Sort columns by date (most recent first)
        df = df.sort_index(axis=1, ascending=False)
        
        logger.success(f"✅ Parsed {sheet_name}: {len(df)} fields × {len(df.columns)} periods")
        
        return df
    
    def parse_income_statement(self) -> Optional[pd.DataFrame]:
        """Parse Income Statement."""
        # Try common Bloomberg sheet names for income statement
        possible_names = [
            'Income - Adjusted',
            'Income Statement',
            'Income - Standardized',
            'IS'
        ]
        
        for name in possible_names:
            if name in self.sheet_names:
                return self.parse_financial_statement(name)
        
        logger.warning("Income Statement sheet not found")
        return None
    
    def parse_balance_sheet(self) -> Optional[pd.DataFrame]:
        """Parse Balance Sheet."""
        possible_names = [
            'Bal Sheet - Standardized',
            'Balance Sheet',
            'Bal Sheet - Adjusted',
            'BS'
        ]
        
        for name in possible_names:
            if name in self.sheet_names:
                return self.parse_financial_statement(name)
        
        logger.warning("Balance Sheet not found")
        return None
    
    def parse_cash_flow(self) -> Optional[pd.DataFrame]:
        """Parse Cash Flow Statement."""
        possible_names = [
            'Cash Flow - Standardized',
            'Cash Flow Statement',
            'Cash Flow - Adjusted',
            'CF'
        ]
        
        for name in possible_names:
            if name in self.sheet_names:
                return self.parse_financial_statement(name)
        
        logger.warning("Cash Flow Statement not found")
        return None
    
    def parse_stock_prices(self) -> Optional[pd.DataFrame]:
        """
        Parse stock price data from Bloomberg export.
        
        Returns:
            DataFrame with dates as index and price columns
        """
        logger.info("Parsing stock prices from Bloomberg file...")
        
        # Try to find price sheet
        possible_names = ['Sheet1', 'Prices', 'Stock Prices', 'Historical Prices']
        
        sheet_name = None
        for name in possible_names:
            if name in self.sheet_names:
                sheet_name = name
                break
        
        if not sheet_name:
            logger.warning("Stock price sheet not found")
            return None
        
        # Read the sheet
        df_raw = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)
        
        # Check if it has a placeholder (but data might still exist)
        has_placeholder = df_raw.iloc[4, 1] == '#N/A Requesting Data...'
        if has_placeholder:
            logger.debug("   Note: Sheet has Bloomberg data request placeholder, checking for actual data...")
        
        # Extract dates and prices
        # Row structure:
        #   Row 0: Start Date | date value
        #   Row 1: End Date | NaN
        #   Row 2-4: Metadata
        #   Row 5: "Dates" | "PX_LAST" (header)
        #   Row 6+: date | price
        
        dates = []
        prices = []
        
        for idx in range(6, len(df_raw)):
            date_val = df_raw.iloc[idx, 0]
            price_val = df_raw.iloc[idx, 1]
            
            if pd.notna(date_val) and pd.notna(price_val):
                try:
                    # Convert to datetime
                    if isinstance(date_val, str):
                        date_obj = pd.to_datetime(date_val)
                    else:
                        date_obj = pd.Timestamp(date_val)
                    
                    dates.append(date_obj)
                    prices.append(float(price_val))
                except:
                    continue
        
        if not dates:
            logger.warning("No valid stock price data found")
            return None
        
        # Create DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Close': prices  # Use 'Close' to match yfinance convention
        })
        df.set_index('Date', inplace=True)
        df.sort_index(ascending=True, inplace=True)  # Chronological order
        
        logger.success(f"✅ Parsed stock prices: {len(df)} data points ({df.index[0].date()} to {df.index[-1].date()})")
        
        return df
    
    def parse_financial_metrics(self) -> Optional[pd.DataFrame]:
        """
        Parse pre-calculated financial metrics sheet (ratios, multiples).
        
        Returns:
            DataFrame with metrics as rows and periods as columns
        """
        logger.info("Parsing financial metrics from Bloomberg file...")
        
        # Try to find metrics sheet
        possible_names = ['FM S1-25-26', 'Financial Metrics', 'Ratios', 'Metrics']
        
        sheet_name = None
        for name in possible_names:
            if name in self.sheet_names:
                sheet_name = name
                break
        
        if not sheet_name:
            logger.warning("Financial metrics sheet not found")
            return None
        
        # Use the same parsing logic as financial statements
        # FM sheets have the same structure
        df = self.parse_financial_statement(sheet_name)
        
        if df is not None:
            logger.success(f"✅ Parsed financial metrics: {len(df)} metrics × {len(df.columns)} periods")
        
        return df
    
    def parse_all_statements(self) -> Dict[str, pd.DataFrame]:
        """
        Parse all financial statements and additional data.
        
        Returns:
            Dictionary with keys: 'income_statement', 'balance_sheet', 'cash_flow', 
            'stock_prices' (optional), 'financial_metrics' (optional)
        """
        logger.info("Parsing all data from Bloomberg file...")
        
        data = {}
        
        # Financial Statements
        income = self.parse_income_statement()
        if income is not None:
            data['income_statement'] = income
        
        balance = self.parse_balance_sheet()
        if balance is not None:
            data['balance_sheet'] = balance
        
        cash_flow = self.parse_cash_flow()
        if cash_flow is not None:
            data['cash_flow'] = cash_flow
        
        # Stock Prices (optional - may not be present or may be placeholder)
        stock_prices = self.parse_stock_prices()
        if stock_prices is not None:
            data['stock_prices'] = stock_prices
        
        # Financial Metrics (optional)
        metrics = self.parse_financial_metrics()
        if metrics is not None:
            data['financial_metrics'] = metrics
        
        logger.success(f"✅ Parsed {len(data)} datasets from Bloomberg")
        
        return data
    
    def get_company_name(self) -> str:
        """Extract company name from the file."""
        # Read first sheet
        first_sheet = self.sheet_names[0]
        df = pd.read_excel(self.file_path, sheet_name=first_sheet, header=None)
        company_name = df.iloc[0, 0]
        
        # Handle NaN or empty values
        if pd.isna(company_name) or str(company_name).strip() == '':
            # Try to extract from filename
            filename = self.file_path.stem  # Get filename without extension
            company_name = filename.split('-')[0] if '-' in filename else filename
        else:
            company_name = str(company_name)
            # Extract just the company name (remove ticker and " - Adjusted/Standardized")
            if ' (' in company_name:
                company_name = company_name.split(' (')[0]
        
        return company_name.strip()


def detect_bloomberg_file(ticker: str, data_dir: str = None) -> Optional[str]:
    """
    Detect if a Bloomberg file exists for the given ticker.
    
    Searches in:
    1. data/bloomberg/ directory
    2. Downloads folder
    3. Current directory
    
    Args:
        ticker: Stock ticker symbol
        data_dir: Optional custom data directory
    
    Returns:
        Path to Bloomberg file if found, None otherwise
    """
    search_dirs = []
    
    # Add custom data dir
    if data_dir:
        search_dirs.append(Path(data_dir))
    
    # Add default locations
    search_dirs.extend([
        Path('data/bloomberg'),
        Path.home() / 'Downloads',
        Path('.')
    ])
    
    # Search patterns
    patterns = [
        f"*{ticker}*.xlsx",
        f"*{ticker.upper()}*.xlsx",
        f"*{ticker.lower()}*.xlsx",
    ]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        
        for pattern in patterns:
            matches = list(search_dir.glob(pattern))
            if matches:
                # Return the most recent file
                latest_file = max(matches, key=lambda p: p.stat().st_mtime)
                logger.info(f"📊 Found Bloomberg file: {latest_file.name}")
                return str(latest_file)
    
    return None


def parse_bloomberg_file(file_path: str) -> Dict:
    """
    Main function to parse a Bloomberg file.
    
    Args:
        file_path: Path to Bloomberg Excel file
    
    Returns:
        Dictionary containing parsed data:
        - company_name: str
        - data: Dict[str, DataFrame] with keys:
          - income_statement (required)
          - balance_sheet (required)
          - cash_flow (required)
          - stock_prices (optional)
          - financial_metrics (optional)
        - data_source: 'bloomberg'
        - file_path: str
    """
    logger.info(f"🔍 Parsing Bloomberg file: {Path(file_path).name}")
    
    parser = BloombergParser(file_path)
    
    result = {
        'company_name': parser.get_company_name(),
        'data': parser.parse_all_statements(),
        'data_source': 'bloomberg',
        'file_path': str(file_path)
    }
    
    logger.success(f"✅ Successfully parsed Bloomberg data for {result['company_name']}")
    
    return result


if __name__ == "__main__":
    # Test the parser
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default test file
        file_path = Path.home() / 'Downloads' / 'Tata Steel Ltd-FS,DVD,Price.xlsx'
    
    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("BLOOMBERG PARSER TEST")
    print("=" * 70)
    
    # Parse the file
    data = parse_bloomberg_file(str(file_path))
    
    print(f"\n✅ Company: {data['company_name']}")
    print(f"✅ Data source: {data['data_source']}")
    print(f"\n📊 Parsed Data ({len(data['data'])} datasets):")
    
    for data_name, df in data['data'].items():
        print(f"\n  {data_name.upper().replace('_', ' ')}:")
        
        if data_name == 'stock_prices':
            # Stock prices have different structure (time series)
            print(f"    Shape: {len(df)} data points")
            print(f"    Date range: {df.index[0].date()} to {df.index[-1].date()}")
            print(f"    Price range: ₹{df['Close'].min():.2f} - ₹{df['Close'].max():.2f}")
            print(f"    Latest price: ₹{df['Close'].iloc[-1]:.2f}")
        else:
            # Financial statements and metrics
            print(f"    Shape: {df.shape[0]} fields × {df.shape[1]} periods")
            print(f"    Periods: {list(df.columns[:3])} ... {list(df.columns[-1:])}")
            print(f"    Sample fields:")
            for field in df.index[:5]:
                print(f"      - {field}")
    
    print("\n✅ Parser test complete!")

