"""
Agents Package.

LangGraph workflow components for equity research report generation:
1. state.py - EquityResearchState schema (shared state)
2. graph.py - StateGraph definition and workflow
3. nodes/ - Three node functions:
   - data_collection.py - Fetches data (deterministic)
   - financial_analysis.py - Calculates ratios, beta, CAPM, DDM (deterministic)
   - report_writing.py - Synthesizes insights with LLM (agent-powered)
"""

from .state import (
    EquityResearchState,
    create_initial_state,
    validate_input_state,
    validate_data_collection_output,
    validate_analysis_output,
    validate_report_output,
    get_state_summary
)

__all__ = [
    'EquityResearchState',
    'create_initial_state',
    'validate_input_state',
    'validate_data_collection_output',
    'validate_analysis_output',
    'validate_report_output',
    'get_state_summary'
]

