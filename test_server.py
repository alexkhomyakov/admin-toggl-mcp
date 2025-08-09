#!/usr/bin/env python3
"""
Test script to verify the Toggl MCP server setup.
"""

import asyncio
import os
import sys

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        from src.toggl_server.main import AdminTogglServer, main
        from src.toggl_server.toggl_api import TogglAPI, TogglAPIError
        from src.toggl_server.models import TogglTimeEntry, TogglWorkspace
        from src.toggl_server.utils import parse_time_entry_response, format_duration
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_server_creation():
    """Test that the server can be created without errors."""
    try:
        from src.toggl_server.main import AdminTogglServer
        server = AdminTogglServer()
        print("✅ Server creation successful")
        return True
    except Exception as e:
        print(f"❌ Server creation error: {e}")
        return False

def test_api_creation():
    """Test that the API client can be created without errors."""
    try:
        from src.toggl_server.toggl_api import TogglAPI
        # This should fail due to missing token, but not due to import issues
        try:
            api = TogglAPI()
            print("❌ API creation should have failed due to missing token")
            return False
        except Exception as e:
            if "TOGGL_API_TOKEN" in str(e):
                print("✅ API creation correctly requires token")
                return True
            else:
                print(f"❌ Unexpected API creation error: {e}")
                return False
    except Exception as e:
        print(f"❌ API import error: {e}")
        return False

def test_model_creation():
    """Test that models can be created without errors."""
    try:
        from src.toggl_server.models import TogglWorkspace, TogglTimeEntry
        from datetime import datetime
        
        # Test workspace creation
        workspace = TogglWorkspace(
            id=1,
            name="Test Workspace",
            premium=False,
            admin=True
        )
        print("✅ Workspace model creation successful")
        
        # Test time entry creation
        time_entry = TogglTimeEntry(
            id=1,
            description="Test Entry",
            start=datetime.now(),
            duration=3600
        )
        print("✅ Time entry model creation successful")
        return True
    except Exception as e:
        print(f"❌ Model creation error: {e}")
        return False

async def test_async_functions():
    """Test that async functions can be defined without errors."""
    try:
        from src.toggl_server.main import main
        print("✅ Async main function import successful")
        return True
    except Exception as e:
        print(f"❌ Async function error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Toggl MCP Server Setup")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Server Creation Test", test_server_creation),
        ("API Creation Test", test_api_creation),
        ("Model Creation Test", test_model_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    # Test async functions
    print(f"\n🔍 Running Async Function Test...")
    try:
        asyncio.run(test_async_functions())
        passed += 1
    except Exception as e:
        print(f"❌ Async function test failed: {e}")
    
    total += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The server is ready to use.")
        print("\nTo use the server:")
        print("1. Set your Toggl API token: export TOGGL_API_TOKEN='your_token_here'")
        print("2. Run the server: python server.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
