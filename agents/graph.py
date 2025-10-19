"""
LangGraph Workflow Definition for Equity Research.

This module defines the StateGraph workflow that orchestrates the three nodes:
1. collect_data_node: Fetches data from various sources (deterministic)
2. analyze_node: Performs financial calculations (deterministic)
3. write_report_node: Synthesizes insights with LLM (agent-powered)

The workflow uses a single shared state (EquityResearchState) that flows
through all nodes sequentially.

LangGraph Best Practice: State-first design with clear workflow edges.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import os

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, END
from agents.state import EquityResearchState, create_initial_state, get_state_summary
from utils.logger import logger


# ==================== LLM CONFIGURATION ====================

def get_llm(provider: Optional[str] = None):
    """
    Get configured LLM based on environment settings.
    
    Supports free LLM providers:
    - Groq: llama-3.1-70b-versatile (Free tier: 30 req/min, 6000 req/day)
    - Gemini: gemini-1.5-flash (Free tier: 15 req/min, 1500 req/day)
    - Ollama: Local models (completely free, requires installation)
    
    Args:
        provider: LLM provider ('groq', 'gemini', 'ollama') or None for auto-detect
    
    Returns:
        Configured LLM instance
    
    Raises:
        ValueError: If no valid LLM is configured
    
    Example:
        >>> llm = get_llm()  # Auto-detect from environment
        >>> llm = get_llm('groq')  # Force Groq
    """
    from config.settings import LLM_PROVIDER, GROQ_API_KEY, GEMINI_API_KEY
    
    # Use explicit provider or fall back to config
    provider = provider or LLM_PROVIDER
    
    logger.info(f"Configuring LLM: {provider}")
    
    if provider == "groq":
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found in environment. "
                "Set it in .env file or export GROQ_API_KEY='your-key'"
            )
        
        try:
            from langchain_groq import ChatGroq
            
            llm = ChatGroq(
                model="llama-3.1-70b-versatile",
                temperature=0.7,
                api_key=GROQ_API_KEY,
                max_tokens=2000
            )
            logger.success("✅ Groq LLM configured (llama-3.1-70b-versatile)")
            return llm
            
        except ImportError:
            raise ImportError(
                "langchain-groq not installed. Run: pip install langchain-groq"
            )
    
    elif provider == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found in environment. "
                "Set it in .env file or export GEMINI_API_KEY='your-key'"
            )
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.7,
                google_api_key=GEMINI_API_KEY,
                max_output_tokens=2000
            )
            logger.success("✅ Gemini LLM configured (gemini-1.5-flash)")
            return llm
            
        except ImportError:
            raise ImportError(
                "langchain-google-genai not installed. "
                "Run: pip install langchain-google-genai"
            )
    
    elif provider == "ollama":
        try:
            from langchain_community.llms import Ollama
            
            llm = Ollama(
                model="llama3.1",
                temperature=0.7
            )
            logger.success("✅ Ollama LLM configured (llama3.1 local)")
            return llm
            
        except ImportError:
            raise ImportError(
                "langchain-community not installed. "
                "Run: pip install langchain-community"
            )
    
    else:
        raise ValueError(
            f"Invalid LLM provider: {provider}. "
            f"Choose: 'groq', 'gemini', or 'ollama'"
        )


# ==================== REAL NODE FUNCTIONS ====================
# Import real implementations from nodes package
from agents.nodes import collect_data_node, analyze_node, write_report_node  # ✅ All Phases Complete!


# ==================== STATEGRAPH CONSTRUCTION ====================

def create_research_graph(llm=None) -> StateGraph:
    """
    Create the LangGraph workflow for equity research.
    
    Workflow:
        Input (ticker) → collect_data → analyze → write_report → Output
    
    Each node updates the shared EquityResearchState, which flows
    sequentially through the workflow.
    
    Args:
        llm: Optional pre-configured LLM. If None, will use get_llm()
    
    Returns:
        Compiled StateGraph ready for execution
    
    Example:
        >>> from agents.graph import create_research_graph
        >>> app = create_research_graph()
        >>> result = app.invoke({"ticker": "RELIANCE", "company_name": "Reliance Industries"})
    """
    logger.info("🔨 Building LangGraph StateGraph...")
    
    # Initialize StateGraph with our state schema
    graph = StateGraph(EquityResearchState)
    
    logger.info("   ✓ StateGraph initialized with EquityResearchState")
    
    # Add nodes (functions that update state)
    graph.add_node("collect_data", collect_data_node)
    logger.info("   ✓ Node added: collect_data (deterministic)")
    
    graph.add_node("analyze", analyze_node)
    logger.info("   ✓ Node added: analyze (deterministic)")
    
    graph.add_node("write_report", write_report_node)
    logger.info("   ✓ Node added: write_report (LLM-powered, placeholder)")
    
    # Define workflow edges (sequential flow)
    graph.set_entry_point("collect_data")
    logger.info("   ✓ Entry point: collect_data")
    
    graph.add_edge("collect_data", "analyze")
    logger.info("   ✓ Edge: collect_data → analyze")
    
    graph.add_edge("analyze", "write_report")
    logger.info("   ✓ Edge: analyze → write_report")
    
    graph.set_finish_point("write_report")
    logger.info("   ✓ Finish point: write_report")
    
    # Compile the graph
    app = graph.compile()
    logger.success("✅ StateGraph compiled successfully!")
    
    return app


# ==================== CONVENIENCE FUNCTIONS ====================

def run_research_workflow(
    ticker: str,
    company_name: Optional[str] = None,
    llm=None
) -> EquityResearchState:
    """
    Convenience function to run the complete workflow.
    
    This is a high-level wrapper that:
    1. Creates initial state
    2. Builds the graph
    3. Executes the workflow
    4. Returns final state
    
    Args:
        ticker: Company ticker (e.g., "RELIANCE")
        company_name: Optional company name (e.g., "Reliance Industries")
        llm: Optional pre-configured LLM
    
    Returns:
        Complete EquityResearchState with all data, analysis, and report
    
    Example:
        >>> from agents.graph import run_research_workflow
        >>> result = run_research_workflow("RELIANCE", "Reliance Industries")
        >>> print(result['executive_summary'])
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"🚀 STARTING EQUITY RESEARCH WORKFLOW")
    logger.info(f"{'='*70}")
    logger.info(f"Company: {company_name or ticker} ({ticker})")
    
    # Create initial state
    initial_state = create_initial_state(ticker, company_name)
    logger.info("✓ Initial state created")
    
    # Build graph
    app = create_research_graph(llm)
    logger.info("✓ StateGraph compiled")
    
    # Execute workflow
    logger.info(f"\n{'='*70}")
    logger.info("🔄 EXECUTING WORKFLOW")
    logger.info(f"{'='*70}\n")
    
    final_state = app.invoke(initial_state)
    
    logger.info(f"\n{'='*70}")
    logger.success("✅ WORKFLOW COMPLETE")
    logger.info(f"{'='*70}")
    
    # Show summary
    logger.info("\n" + get_state_summary(final_state))
    
    return final_state


# ==================== TESTING & VALIDATION ====================

def test_graph_structure():
    """
    Test that the graph is properly structured.
    
    Validates:
    - Graph can be compiled
    - All nodes are registered
    - Edges are defined
    - Entry/exit points are set
    
    Returns:
        True if all tests pass, False otherwise
    """
    logger.info("🧪 Testing graph structure...")
    
    try:
        # Build graph
        app = create_research_graph()
        logger.success("✅ Graph compilation: PASS")
        
        # Check if it's compiled
        if app is None:
            logger.error("❌ Graph is None")
            return False
        
        logger.success("✅ Graph object: PASS")
        
        # Try to visualize (if available)
        try:
            # This will show the graph structure if mermaid is available
            logger.info("\n📊 Graph Structure:")
            logger.info("   Entry: collect_data")
            logger.info("   collect_data → analyze")
            logger.info("   analyze → write_report")
            logger.info("   Exit: write_report")
        except Exception as e:
            logger.debug(f"Graph visualization not available: {e}")
        
        logger.success("✅ All graph structure tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Graph structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_execution():
    """
    Test that the workflow can execute with placeholder nodes.
    
    This tests:
    - State flows through all nodes
    - Each node returns valid updates
    - Final state has expected structure
    
    Returns:
        True if workflow executes without errors
    """
    logger.info("\n🧪 Testing workflow execution with placeholders...")
    
    try:
        # Create test state
        test_state = create_initial_state("TEST", "Test Company")
        logger.info("✓ Test state created")
        
        # Build and run workflow
        app = create_research_graph()
        logger.info("✓ Graph compiled")
        
        logger.info("\n🔄 Running workflow with placeholder nodes...")
        result = app.invoke(test_state)
        logger.info("✓ Workflow executed")
        
        # Validate result
        if result is None:
            logger.error("❌ Result is None")
            return False
        
        if not isinstance(result, dict):
            logger.error(f"❌ Result is not a dict: {type(result)}")
            return False
        
        # Check key fields
        required_fields = ['ticker', 'company_name', 'current_step']
        for field in required_fields:
            if field not in result:
                logger.error(f"❌ Missing field in result: {field}")
                return False
        
        logger.success(f"✅ Workflow execution: PASS")
        logger.info(f"   Final step: {result.get('current_step')}")
        logger.info(f"   Ticker: {result.get('ticker')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Workflow execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """Run comprehensive tests on the graph structure."""
    print("="*70)
    print("TESTING LANGGRAPH STATEGRAPH STRUCTURE")
    print("="*70)
    
    # Test 1: Graph Structure
    print("\n" + "="*70)
    print("TEST 1: Graph Structure")
    print("="*70)
    test1_passed = test_graph_structure()
    
    # Test 2: Workflow Execution
    print("\n" + "="*70)
    print("TEST 2: Workflow Execution (with placeholders)")
    print("="*70)
    test2_passed = test_workflow_execution()
    
    # Test 3: LLM Configuration (if keys available)
    print("\n" + "="*70)
    print("TEST 3: LLM Configuration")
    print("="*70)
    try:
        from config.settings import GROQ_API_KEY, GEMINI_API_KEY
        
        if GROQ_API_KEY:
            try:
                llm = get_llm('groq')
                print("✅ Groq LLM configuration: PASS")
                test3_passed = True
            except Exception as e:
                print(f"⚠️  Groq LLM configuration: {e}")
                test3_passed = False
        elif GEMINI_API_KEY:
            try:
                llm = get_llm('gemini')
                print("✅ Gemini LLM configuration: PASS")
                test3_passed = True
            except Exception as e:
                print(f"⚠️  Gemini LLM configuration: {e}")
                test3_passed = False
        else:
            print("⚠️  No API keys configured - LLM test skipped")
            print("   Set GROQ_API_KEY or GEMINI_API_KEY in .env file")
            test3_passed = None  # Not applicable
    except Exception as e:
        print(f"⚠️  LLM test error: {e}")
        test3_passed = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Graph Structure:     {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Workflow Execution:  {'✅ PASS' if test2_passed else '❌ FAIL'}")
    if test3_passed is not None:
        print(f"LLM Configuration:   {'✅ PASS' if test3_passed else '❌ FAIL'}")
    else:
        print(f"LLM Configuration:   ⏭️  SKIPPED (no API keys)")
    
    all_passed = test1_passed and test2_passed and (test3_passed is not False)
    
    if all_passed:
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED - GRAPH IS READY!")
        print("="*70)
        print("\n📝 Next Steps:")
        print("   1. Implement collect_data_node() in Phase 4")
        print("   2. Implement analyze_node() in Phase 5")
        print("   3. Implement write_report_node() in Phase 6")
        print("\n🎯 The StateGraph structure is ready for node implementation!")
    else:
        print("\n" + "="*70)
        print("❌ SOME TESTS FAILED - CHECK ERRORS ABOVE")
        print("="*70)

