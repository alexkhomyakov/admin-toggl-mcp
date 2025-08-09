#!/usr/bin/env python3
"""
Test script for the Toggl Claude Connector

This script tests the basic functionality of the connector to ensure it's working correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from connector import server, admin_server, handle_list_tools, handle_call_tool

async def test_connector():
    """Test the connector functionality"""
    print("🧪 Testing Toggl Claude Connector...")
    
    # Test 1: Check if tools are listed correctly
    print("\n1. Testing tool listing...")
    try:
        tools = await handle_list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        return False
    
    # Test 2: Check API initialization
    print("\n2. Testing API initialization...")
    api_token = os.getenv("TOGGL_API_TOKEN")
    if api_token:
        try:
            await admin_server.initialize_apis(api_token)
            print("✅ Toggl APIs initialized successfully")
        except Exception as e:
            print(f"⚠️  API initialization failed: {e}")
            print("   (This is expected if the API token is invalid)")
    else:
        print("⚠️  No TOGGL_API_TOKEN found - API features will be limited")
    
    # Test 3: Test basic tool calls (without API)
    print("\n3. Testing tool call handling...")
    try:
        # Test list_workspaces without API
        result = await handle_call_tool("list_workspaces", {})
        print("✅ Tool call handling works")
        print(f"   Response: {result[0].text[:100]}...")
    except Exception as e:
        print(f"❌ Error in tool call handling: {e}")
        return False
    
    print("\n🎉 Connector test completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set your TOGGL_API_TOKEN environment variable")
    print("2. Install the connector in Claude Desktop")
    print("3. Start using Toggl tools in your conversations!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_connector())
    sys.exit(0 if success else 1)
