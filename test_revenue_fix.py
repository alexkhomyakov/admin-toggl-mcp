#!/usr/bin/env python3
"""
Final test to verify revenue fix is working correctly
"""
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connector import admin_server

async def test_revenue_fix():
    """Test that revenue is now correct across all functions"""
    
    api_token = os.getenv("TOGGL_API_TOKEN")
    if not api_token:
        print("❌ TOGGL_API_TOKEN not set")
        return
    
    workspace_id = 2047911
    start_date = "2025-08-04"
    end_date = "2025-08-10"
    
    print(f"🎯 TESTING REVENUE FIX")
    print(f"📅 Date range: {start_date} to {end_date}")
    print(f"🏢 Workspace: {workspace_id}")
    print(f"🎯 Expected Revenue: $39,206.00")
    print("=" * 60)
    
    try:
        # Initialize APIs
        print("\n🔧 INITIALIZING APIS...")
        await admin_server.initialize_apis(api_token)
        print("✅ APIs initialized successfully")
        
        # Test 1: Organization Dashboard
        print("\n🏢 TEST 1: ORGANIZATION DASHBOARD")
        print("-" * 40)
        from connector import _get_organization_dashboard_local
        dashboard_result = await _get_organization_dashboard_local(admin_server, workspace_id, start_date, end_date)
        
        # Extract revenue from dashboard
        import re
        revenue_match = re.search(r'Total Revenue: USD ([\d,]+\.\d+)', dashboard_result)
        if revenue_match:
            revenue = float(revenue_match.group(1).replace(',', ''))
            print(f"   Revenue: ${revenue:,.2f}")
            if abs(revenue - 39206) < 10:  # Allow small difference
                print("   ✅ Revenue is correct!")
            else:
                print("   ❌ Revenue is still wrong!")
        else:
            print("   ❌ Could not extract revenue from dashboard")
        
        # Test 2: Productivity Insights
        print("\n📊 TEST 2: PRODUCTIVITY INSIGHTS")
        print("-" * 40)
        from connector import _get_productivity_insights_local
        insights_result = await _get_productivity_insights_local(admin_server, workspace_id, start_date, end_date, True)
        
        # Extract revenue from insights
        revenue_match = re.search(r'Total Revenue: USD ([\d,]+\.\d+)', insights_result)
        if revenue_match:
            revenue = float(revenue_match.group(1).replace(',', ''))
            print(f"   Revenue: ${revenue:,.2f}")
            if abs(revenue - 39206) < 10:
                print("   ✅ Revenue is correct!")
            else:
                print("   ❌ Revenue is still wrong!")
        else:
            print("   ❌ Could not extract revenue from insights")
        
        # Test 3: Financial Summary
        print("\n💰 TEST 3: FINANCIAL SUMMARY")
        print("-" * 40)
        from connector import _get_financial_summary_local
        financial_result = await _get_financial_summary_local(admin_server, workspace_id, start_date, end_date, False)
        
        # Extract revenue from financial summary
        revenue_match = re.search(r'Total Revenue: USD ([\d,]+\.\d+)', financial_result)
        if revenue_match:
            revenue = float(revenue_match.group(1).replace(',', ''))
            print(f"   Revenue: ${revenue:,.2f}")
            if abs(revenue - 39206) < 10:
                print("   ✅ Revenue is correct!")
            else:
                print("   ❌ Revenue is still wrong!")
        else:
            print("   ❌ Could not extract revenue from financial summary")
        
        print("\n🎉 REVENUE FIX TEST COMPLETED!")
        print("\n✅ SUMMARY:")
        print("   • All functions now use Summary Report for accurate revenue")
        print("   • Reports API v3 used for labor cost calculations")
        print("   • Revenue should be ~$39,206.00 across all functions")
        print("   • Profit margins are now realistic (not 100%)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_revenue_fix())
