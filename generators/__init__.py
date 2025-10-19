"""
Document Generators Package.

This package contains modules to generate final deliverables:
1. word_generator.py - Generate Word document (.docx)
2. excel_generator.py - Generate Excel workbook (.xlsx)

Both generators take the complete EquityResearchState and produce
professional documents following the assignment template.
"""

from .word_generator import generate_word_report
from .excel_generator import generate_excel_workbook

__all__ = ['generate_word_report', 'generate_excel_workbook']

