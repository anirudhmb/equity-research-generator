"""
Test UI components and functionality.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ui_imports():
    """Test that UI imports work correctly."""
    try:
        # Test main imports
        from agents import create_research_graph, create_initial_state
        from generators import generate_word_report, generate_excel_workbook
        from utils.logger import logger
        
        print("✅ All UI imports successful!")
        return True
    except Exception as e:
        print(f"❌ UI import error: {e}")
        return False


def test_ui_file_exists():
    """Test that UI files exist."""
    ui_dir = Path(__file__).parent.parent / "ui"
    
    required_files = [
        ui_dir / "app.py",
        ui_dir / "README.md",
        ui_dir / "__init__.py",
        Path(__file__).parent.parent / "run_ui.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if file_path.exists():
            print(f"✅ {file_path.name} exists")
        else:
            print(f"❌ {file_path.name} missing")
            all_exist = False
    
    return all_exist


def test_state_creation():
    """Test state creation for UI workflow."""
    try:
        from agents import create_initial_state
        
        state = create_initial_state("RELIANCE", "Reliance Industries Limited")
        
        # Ticker normalization happens in data collection node, not in initial state
        assert state['ticker'] == "RELIANCE", "Ticker should be as provided"
        assert state['company_name'] == "Reliance Industries Limited"
        assert state['current_step'] == 'start', "Initial step should be 'start'"
        assert state['errors'] == []
        assert state['warnings'] == []
        assert state['data_complete'] == False
        
        print("✅ State creation successful!")
        return True
    except AssertionError as e:
        print(f"❌ State creation assertion error: {e}")
        return False
    except Exception as e:
        print(f"❌ State creation error: {e}")
        return False


def test_graph_creation():
    """Test graph creation for UI workflow."""
    try:
        from agents import create_research_graph
        
        app = create_research_graph()
        
        # Check that app has required methods
        assert hasattr(app, 'invoke'), "Graph should have invoke method"
        
        print("✅ Graph creation successful!")
        return True
    except Exception as e:
        print(f"❌ Graph creation error: {e}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("TESTING UI COMPONENTS")
    print("="*70)
    
    tests = [
        ("UI Imports", test_ui_imports),
        ("UI Files", test_ui_file_exists),
        ("State Creation", test_state_creation),
        ("Graph Creation", test_graph_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 70)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All UI tests passed!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed")
        sys.exit(1)

