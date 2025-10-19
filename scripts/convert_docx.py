#!/usr/bin/env python3
"""Convert DOCX files to Markdown format."""

import mammoth
import sys
from pathlib import Path


def convert_docx_to_markdown(docx_path, output_path):
    """Convert a DOCX file to Markdown."""
    try:
        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            markdown = result.value
            
            # Write to output file
            with open(output_path, "w", encoding="utf-8") as md_file:
                md_file.write(markdown)
            
            print(f"✓ Converted: {docx_path} -> {output_path}")
            
            # Print any warnings
            if result.messages:
                print(f"  Warnings for {docx_path}:")
                for message in result.messages:
                    print(f"    - {message}")
            
            return True
    except Exception as e:
        print(f"✗ Error converting {docx_path}: {e}")
        return False


def main():
    base_dir = Path(__file__).parent
    
    # Files to convert
    files = [
        ("Equity Research Report Guidelines.docx", "Equity_Research_Report_Guidelines.md"),
        ("Equity Research Report-Template.docx", "Equity_Research_Report_Template.md")
    ]
    
    print("Converting DOCX files to Markdown...\n")
    
    for docx_file, md_file in files:
        docx_path = base_dir / docx_file
        md_path = base_dir / md_file
        
        if docx_path.exists():
            convert_docx_to_markdown(docx_path, md_path)
        else:
            print(f"✗ File not found: {docx_path}")
    
    print("\nConversion complete!")


if __name__ == "__main__":
    main()

