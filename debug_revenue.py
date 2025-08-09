#!/usr/bin/env python3
"""
Debug script to investigate revenue calculation issues
"""
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.toggl_server.reports_api import TogglReportsAPI

async def debug_revenue():
    """Debug revenue calculation issues"""
    
    api_token = os.getenv("TOGGL_API_TOKEN")
    if not api_token:
        print("❌ TOGGL_API_TOKEN not set")
        return
    
    workspace_id = 2047911
    start_date = "2025-08-04"
    end_date = "2025-08-10"
    
    print(f"🔍 DEBUGGING REVENUE CALCULATION")
    print(f"📅 Date range: {start_date} to {end_date}")
    print(f"🏢 Workspace: {workspace_id}")
    print(f"🎯 Expected Revenue: $39,206.00")
    print("=" * 60)
    
    try:
        api = TogglReportsAPI(api_token)
        
        # Test 1: Get detailed entries from Reports API v3
        print("\n📋 TEST 1: REPORTS API V3 DETAILED ENTRIES")
        print("-" * 40)
        
        detailed_entries = await api.get_detailed_report_v3(workspace_id, start_date, end_date, hide_amounts=False)
        print(f"✅ Got {len(detailed_entries)} detailed entries")
        
        # Calculate total revenue from detailed entries
        total_revenue_v3 = 0
        total_entries_with_revenue = 0
        
        for entry in detailed_entries:
            billable_amount_cents = entry.get('billable_amount_in_cents', 0)
            billable_amount_dollars = billable_amount_cents / 100
            total_revenue_v3 += billable_amount_dollars
            
            if billable_amount_cents > 0:
                total_entries_with_revenue += 1
                print(f"   Entry: {entry.get('description', 'Unknown')[:50]}... - ${billable_amount_dollars:.2f}")
        
        print(f"\n📊 REPORTS API V3 RESULTS:")
        print(f"   • Total Revenue: ${total_revenue_v3:,.2f}")
        print(f"   • Entries with revenue: {total_entries_with_revenue}/{len(detailed_entries)}")
        print(f"   • Expected: $39,206.00")
        print(f"   • Difference: ${total_revenue_v3 - 39206:.2f}")
        
        # Test 2: Check if we need to use a different date range
        print("\n📅 TEST 2: CHECKING DATE RANGE")
        print("-" * 40)
        
        # Try different date ranges
        date_ranges = [
            ("2025-08-01", "2025-08-07"),  # Previous week
            ("2025-08-05", "2025-08-11"),  # Next week
            ("2025-08-03", "2025-08-09"),  # Slightly different
        ]
        
        for start, end in date_ranges:
            entries = await api.get_detailed_report_v3(workspace_id, start, end, hide_amounts=False)
            revenue = sum(entry.get('billable_amount_in_cents', 0) / 100 for entry in entries)
            print(f"   {start} to {end}: ${revenue:,.2f} ({len(entries)} entries)")
        
        # Test 3: Check if we need to use summary report instead
        print("\n📊 TEST 3: COMPARING WITH SUMMARY REPORT")
        print("-" * 40)
        
        summary_data = await api.get_summary_report(workspace_id, start_date, end_date, "projects")
        print(f"Summary data keys: {list(summary_data.keys())}")
        
        total_grand = summary_data.get('total_grand', 0)
        total_billable = summary_data.get('total_billable', 0)
        
        print(f"   • Total Grand: {total_grand} (milliseconds)")
        print(f"   • Total Billable: {total_billable} (milliseconds)")
        
        # Calculate revenue from summary data
        total_revenue_summary = 0
        for project in summary_data.get('data', []):
            for currency_info in project.get('total_currencies', []):
                amount = currency_info.get('amount', 0)
                total_revenue_summary += amount
                print(f"   Project: {project.get('title', {}).get('project', 'Unknown')} - ${amount:,.2f}")
        
        print(f"\n📊 SUMMARY REPORT RESULTS:")
        print(f"   • Total Revenue: ${total_revenue_summary:,.2f}")
        print(f"   • Expected: $39,206.00")
        print(f"   • Difference: ${total_revenue_summary - 39206:.2f}")
        
        # Test 4: Check if we need to use insights profitability
        print("\n💰 TEST 4: CHECKING INSIGHTS PROFITABILITY")
        print("-" * 40)
        
        insights_data = await api.get_insights_profitability(workspace_id, start_date, end_date, "projects")
        print(f"Insights data keys: {list(insights_data.keys())}")
        
        if 'totals' in insights_data:
            totals = insights_data['totals']
            print(f"   • Totals keys: {list(totals.keys())}")
            for key, value in totals.items():
                print(f"   • {key}: {value}")
        
        await api.close()
        
        print("\n🔍 ANALYSIS:")
        print("   • Reports API v3: ${total_revenue_v3:,.2f}")
        print("   • Summary Report: ${total_revenue_summary:,.2f}")
        print("   • Expected: $39,206.00")
        print("   • The issue might be with date range or API endpoint choice")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_revenue())
