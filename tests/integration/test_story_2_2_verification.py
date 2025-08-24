#!/usr/bin/env python3
"""
Story 2.2 Implementation Verification Test
Tests the new GPT-5 Valuation Agent implementation
"""

import sys
import os
import traceback
from typing import Any

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all new components import correctly."""
    print("=== TESTING IMPORTS ===")
    
    try:
        from src.models.owner_returns import OwnerReturnsValuation, IRRComponents
        print("PASS: OwnerReturns models import successful")
    except Exception as e:
        print(f"FAIL: OwnerReturns models import failed: {e}")
        return False
    
    try:
        from src.agents.valuation_agent import ValuationAgent
        print("PASS: ValuationAgent import successful")
    except Exception as e:
        print(f"FAIL: ValuationAgent import failed: {e}")
        return False
    
    try:
        from src.utils.openai_client import OpenAIClient
        print("PASS: OpenAIClient import successful")
    except Exception as e:
        print(f"FAIL: OpenAIClient import failed: {e}")
        return False
    
    return True

def test_model_creation():
    """Test MVP-friendly model creation with defaults."""
    print("\n=== TESTING MODEL CREATION ===")
    
    try:
        from src.models.owner_returns import OwnerReturnsValuation
        
        # Test creation with minimal data (should work with defaults)
        valuation = OwnerReturnsValuation(ticker="TEST")
        print("PASS: OwnerReturnsValuation created with defaults successfully")
        print(f"   - ticker: {valuation.ticker}")
        print(f"   - irr_analysis: {valuation.irr_analysis}")
        print(f"   - investment_thesis: '{valuation.investment_thesis}'")
        
        return True
    except Exception as e:
        print(f"FAIL: Model creation failed: {e}")
        traceback.print_exc()
        return False

def test_client_methods():
    """Test that OpenAI client has required methods."""
    print("\n=== TESTING CLIENT METHODS ===")
    
    try:
        from src.utils.openai_client import OpenAIClient
        
        # Don't actually initialize (no API key needed for method check)
        client_class = OpenAIClient
        
        # Check for required methods
        required_methods = ['respond', 'respond_with_web_search', 'create_completion']
        missing_methods = []
        
        for method in required_methods:
            if not hasattr(client_class, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"FAIL: Missing methods: {missing_methods}")
            return False
        else:
            print("PASS: All required OpenAIClient methods present:")
            for method in required_methods:
                print(f"   - {method}")
        
        return True
    except Exception as e:
        print(f"FAIL: Client methods check failed: {e}")
        return False

def test_agent_initialization():
    """Test agent initialization without API calls."""
    print("\n=== TESTING AGENT INITIALIZATION ===")
    
    try:
        # Mock the OpenAI client to avoid API key requirement
        import os
        os.environ["OPENAI_API_KEY"] = "test-key-for-init"
        
        from src.agents.valuation_agent import ValuationAgent
        
        agent = ValuationAgent()
        print("PASS: ValuationAgent initialized successfully")
        print(f"   - agent_name: {agent.agent_name}")
        
        # Check for key methods
        key_methods = ['conduct_research', '_run_research_phase', '_run_valuation_phase']
        for method in key_methods:
            if hasattr(agent, method):
                print(f"   - {method}: present")
            else:
                print(f"   - {method}: MISSING")
        
        return True
    except Exception as e:
        print(f"FAIL: Agent initialization failed: {e}")
        traceback.print_exc()
        return False

def test_legacy_bloat_check():
    """Check if legacy bloat still exists."""
    print("\n=== CHECKING FOR LEGACY BLOAT ===")
    
    import os
    
    legacy_files = [
        "src/utils/owner_returns_engine.py",
        # Add other legacy files as identified
    ]
    
    bloat_found = False
    for file_path in legacy_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"WARNING: Legacy file still exists: {file_path} ({file_size} bytes)")
            bloat_found = True
        else:
            print(f"PASS: Legacy file removed: {file_path}")
    
    return not bloat_found

def test_old_vs_new_implementation():
    """Compare old vs new implementation approach."""
    print("\n=== IMPLEMENTATION COMPARISON ===")
    
    # Check if old calculation engine exists
    import os
    old_engine_path = "src/utils/owner_returns_engine.py"
    
    if os.path.exists(old_engine_path):
        old_size = os.path.getsize(old_engine_path)
        print(f"OLD Implementation: {old_engine_path} ({old_size} bytes)")
    else:
        print("OLD Implementation: Properly removed")
    
    # Check new agent size
    new_agent_path = "src/agents/valuation_agent.py"
    if os.path.exists(new_agent_path):
        new_size = os.path.getsize(new_agent_path)
        print(f"NEW Implementation: {new_agent_path} ({new_size} bytes)")
        
        # Check if it's actually using GPT-5 patterns
        with open(new_agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        has_web_search = 'respond_with_web_search' in content
        has_proper_workflow = 'temp_md' in content and 'valuation_md' in content
        has_real_data = 'web_search' in content
        
        print("NEW Implementation Analysis:")
        print(f"   - Uses web search: {'YES' if has_web_search else 'NO'}")
        print(f"   - 2-step workflow: {'YES' if has_proper_workflow else 'NO'}")
        print(f"   - Real data approach: {'YES' if has_real_data else 'NO'}")
        
        return has_web_search and has_proper_workflow and has_real_data
    else:
        print("FAIL: New agent implementation not found")
        return False

def main():
    """Run all verification tests."""
    print("STORY 2.2 IMPLEMENTATION VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Model Creation", test_model_creation), 
        ("Client Methods", test_client_methods),
        ("Agent Initialization", test_agent_initialization),
        ("Legacy Bloat Check", test_legacy_bloat_check),
        ("Implementation Comparison", test_old_vs_new_implementation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"CRASH: {test_name} test failed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("VERIFICATION RESULTS:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\nSUCCESS: ALL TESTS PASSED - Story 2.2 implementation appears to be working!")
        print("Ready for real API integration testing")
    else:
        print("\nFAILURE: SOME TESTS FAILED - Implementation needs fixes")
        
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during verification: {e}")
        traceback.print_exc()
        sys.exit(1)