"""
Node Functions for LangGraph Workflow.

This package contains the three node functions that make up the
equity research workflow:

1. data_collection.py - Collects data from various sources (deterministic)
2. financial_analysis.py - Performs calculations and analysis (deterministic)
3. report_writing.py - Synthesizes insights with LLM (agent-powered)

Each node function:
- Takes EquityResearchState as input
- Returns Dict[str, Any] with state updates
- Is pure and side-effect free (except for logging)
- Handles errors gracefully
"""

from .data_collection import collect_data_node

__all__ = ['collect_data_node']

