#!/usr/bin/env python3
"""Convert DOCX files to PDF format."""

from docx2pdf import convert
from pathlib import Path
import sys


def convert_docx_to_pdf(docx_path, pdf_path):
    """Convert a DOCX file to PDF."""
    try:
        convert(str(docx_path), str(pdf_path))
        print(f"✓ Converted: {docx_path} -> {pdf_path}")
        return True
    except Exception as e:
        print(f"✗ Error converting {docx_path}: {e}")
        return False


def main():
    base_dir = Path(__file__).parent
    
    # Files to convert
    files = [
        ("Equity Research Report Guidelines.docx", "Equity_Research_Report_Guidelines.pdf"),
        ("Equity Research Report-Template.docx", "Equity_Research_Report_Template.pdf")
    ]
    
    print("Converting DOCX files to PDF...\n")
    
    for docx_file, pdf_file in files:
        docx_path = base_dir / docx_file
        pdf_path = base_dir / pdf_file
        
        if docx_path.exists():
            convert_docx_to_pdf(docx_path, pdf_path)
        else:
            print(f"✗ File not found: {docx_path}")
    
    print("\nConversion complete!")


if __name__ == "__main__":
    main()

