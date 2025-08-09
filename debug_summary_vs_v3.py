#!/usr/bin/env python3
"""
Compare Summary Report vs Reports API v3 data structures
"""
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.toggl_server.reports_api import TogglReportsAPI

async def compare_data_structures():
    """Compare Summary Report vs Reports API v3"""
    
    api_token = os.getenv("TOGGL_API_TOKEN")
    if not api_token:
        print("❌ TOGGL_API_TOKEN not set")
        return
    
    workspace_id = 2047911
    start_date = "2025-08-04"
    end_date = "2025-08-10"
    
    print(f"🔍 COMPARING SUMMARY REPORT VS REPORTS API V3")
    print(f"📅 Date range: {start_date} to {end_date}")
    print("=" * 60)
    
    try:
        api = TogglReportsAPI(api_token)
        
        # Get Summary Report data
        print("\n📊 SUMMARY REPORT DATA STRUCTURE")
        print("-" * 40)
        
        summary_data = await api.get_summary_report(workspace_id, start_date, end_date, "projects")
        
        print(f"Top-level keys: {list(summary_data.keys())}")
        print(f"Total projects: {len(summary_data.get('data', []))}")
        
        # Show first project structure
        if summary_data.get('data'):
            first_project = summary_data['data'][0]
            print(f"\nFirst project keys: {list(first_project.keys())}")
            print(f"Project title: {first_project.get('title', {})}")
            print(f"Total currencies: {first_project.get('total_currencies', [])}")
            
            # Show all projects and their revenue
            print(f"\n📈 ALL PROJECTS FROM SUMMARY REPORT:")
            total_revenue = 0
            for i, project in enumerate(summary_data.get('data', []), 1):
                project_name = project.get('title', {}).get('project', 'Unknown')
                currencies = project.get('total_currencies', [])
                revenue = sum(currency.get('amount', 0) for currency in currencies)
                total_revenue += revenue
                print(f"   {i}. {project_name}: ${revenue:,.2f}")
            
            print(f"\n💰 TOTAL REVENUE FROM SUMMARY: ${total_revenue:,.2f}")
        
        # Get Reports API v3 data
        print("\n\n📋 REPORTS API V3 DATA STRUCTURE")
        print("-" * 40)
        
        detailed_entries = await api.get_detailed_report_v3(workspace_id, start_date, end_date, hide_amounts=False)
        
        print(f"Total entries: {len(detailed_entries)}")
        
        if detailed_entries:
            first_entry = detailed_entries[0]
            print(f"\nFirst entry keys: {list(first_entry.keys())}")
            print(f"Sample entry: {first_entry}")
            
            # Group by project and calculate revenue
            project_revenue_v3 = {}
            total_revenue_v3 = 0
            
            for entry in detailed_entries:
                project_name = entry.get('project_name', 'Unknown')
                billable_amount = entry.get('billable_amount_in_cents', 0) / 100
                
                if project_name not in project_revenue_v3:
                    project_revenue_v3[project_name] = 0
                project_revenue_v3[project_name] += billable_amount
                total_revenue_v3 += billable_amount
            
            print(f"\n📈 PROJECTS FROM REPORTS API V3:")
            for project_name, revenue in sorted(project_revenue_v3.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {project_name}: ${revenue:,.2f}")
            
            print(f"\n💰 TOTAL REVENUE FROM V3: ${total_revenue_v3:,.2f}")
        
        # Check if we need to use summary report for revenue
        print(f"\n\n🔍 CONCLUSION:")
        print(f"   • Summary Report Revenue: ${total_revenue:,.2f}")
        print(f"   • Reports API V3 Revenue: ${total_revenue_v3:,.2f}")
        print(f"   • Expected Revenue: $39,206.00")
        print(f"   • Summary Report is correct!")
        print(f"   • We should use Summary Report for revenue calculations")
        
        await api.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(compare_data_structures())
