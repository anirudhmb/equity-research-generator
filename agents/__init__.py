"""
Agents Package.

Contains the three specialized agents for equity research report generation:
1. DataCollectionAgent - Orchestrates data fetching from all sources
2. FinancialAnalysisAgent - Performs calculations and analysis
3. ResearchWritingAgent - Synthesizes insights and generates report content
"""

from .data_agent import DataCollectionAgent

__all__ = ['DataCollectionAgent']

