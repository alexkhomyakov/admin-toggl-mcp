#!/usr/bin/env python3
"""
Test all three main reports for consistency and cross-matching
"""
import asyncio
import os
import sys
import re
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_all_reports_consistency():
    """Test that all reports are consistent with each other"""
    
    try:
        # Import all report functions
        from connector import (
            _get_organization_dashboard_local,
            _get_team_productivity_report_local, 
            _get_project_profitability_analysis_with_processor,
            admin_server
        )
        
        api_token = os.getenv("TOGGL_API_TOKEN")
        if not api_token:
            print("❌ TOGGL_API_TOKEN not set")
            return
        
        # Initialize the admin server
        print("🔧 INITIALIZING ADMIN SERVER...")
        await admin_server.initialize_apis(api_token)
        print("✅ Admin server initialized successfully")
        
        # Test parameters - past week
        workspace_id = 2047911
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        print(f"\n🧪 TESTING ALL REPORTS CONSISTENCY")
        print(f"📅 Date range: {start_date} to {end_date}")
        print(f"🏢 Workspace: {workspace_id}")
        print("=" * 80)
        
        # Test 1: Get Organization Dashboard
        print("\n📊 TEST 1: Organization Dashboard")
        print("   Fetching organization dashboard data...")
        
        try:
            org_dashboard = await _get_organization_dashboard_local(
                admin_server_instance=admin_server,
                workspace_id=workspace_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if org_dashboard:
                print("   ✅ Organization dashboard returned data")
                
                # Extract key metrics from organization dashboard
                org_revenue_match = re.search(r'Total Revenue: USD ([\d,]+\.?\d*)', org_dashboard)
                org_revenue = float(org_revenue_match.group(1).replace(',', '')) if org_revenue_match else 0
                
                org_hours_match = re.search(r'Total Hours: ([\d,]+\.?\d*)h', org_dashboard)
                org_hours = float(org_hours_match.group(1).replace(',', '')) if org_hours_match else 0
                
                # Look for profit in organization dashboard
                org_profit_match = re.search(r'Total Profit: USD ([\d,]+\.?\d*)', org_dashboard)
                org_profit = float(org_profit_match.group(1).replace(',', '')) if org_profit_match else 0
                
                print(f"   📊 Organization Dashboard Metrics:")
                print(f"      Revenue: ${org_revenue:.2f}")
                print(f"      Hours: {org_hours:.2f}h")
                print(f"      Profit: ${org_profit:.2f}")
                
            else:
                print("   ❌ Organization dashboard failed")
                org_revenue = org_hours = org_profit = 0
                
        except Exception as e:
            print(f"   ❌ Error in organization dashboard: {e}")
            org_revenue = org_hours = org_profit = 0
        
        # Test 2: Get Team Productivity Report
        print("\n📊 TEST 2: Team Productivity Report")
        print("   Fetching team productivity report data...")
        
        try:
            team_report = await _get_team_productivity_report_local(
                admin_server_instance=admin_server,
                workspace_id=workspace_id,
                start_date=start_date,
                end_date=end_date,
                include_individual_metrics=True
            )
            
            if team_report:
                print("   ✅ Team productivity report returned data")
                
                # Extract key metrics from team report
                team_revenue_match = re.search(r'Total Revenue: USD ([\d,]+\.?\d*)', team_report)
                team_revenue = float(team_revenue_match.group(1).replace(',', '')) if team_revenue_match else 0
                
                # Team report shows individual hours, not total hours - extract from summary
                team_hours_match = re.search(r'Total Hours: ([\d,]+\.?\d*)h', team_report)
                team_hours = float(team_hours_match.group(1).replace(',', '')) if team_hours_match else 0
                
                # Look for profit in team report
                team_profit_match = re.search(r'Total Profit: USD ([\d,]+\.?\d*)', team_report)
                team_profit = float(team_profit_match.group(1).replace(',', '')) if team_profit_match else 0
                
                print(f"   📊 Team Productivity Report Metrics:")
                print(f"      Revenue: ${team_revenue:.2f}")
                print(f"      Hours: {team_hours:.2f}h")
                print(f"      Profit: ${team_profit:.2f}")
                
            else:
                print("   ❌ Team productivity report failed")
                team_revenue = team_hours = team_profit = 0
                
        except Exception as e:
            print(f"   ❌ Error in team productivity report: {e}")
            team_revenue = team_hours = team_profit = 0
        
        # Test 3: Get Project Profitability Analysis (we already tested this)
        print("\n📊 TEST 3: Project Profitability Analysis")
        print("   Fetching project profitability analysis data...")
        
        try:
            project_report = await _get_project_profitability_analysis_with_processor(
                admin_server_instance=admin_server,
                workspace_id=workspace_id,
                start_date=start_date,
                end_date=end_date,
                sort_by="revenue",
                min_hours=0.0
            )
            
            if project_report:
                print("   ✅ Project profitability analysis returned data")
                
                # Extract key metrics from project report
                proj_revenue_match = re.search(r'Total Revenue: USD ([\d,]+\.?\d*)', project_report)
                proj_revenue = float(proj_revenue_match.group(1).replace(',', '')) if proj_revenue_match else 0
                
                proj_hours_match = re.search(r'Total Hours: ([\d,]+\.?\d*)h', project_report)
                proj_hours = float(proj_hours_match.group(1).replace(',', '')) if proj_hours_match else 0
                
                proj_profit_match = re.search(r'Total Profit: USD ([\d,]+\.?\d*)', project_report)
                proj_profit = float(proj_profit_match.group(1).replace(',', '')) if proj_profit_match else 0
                
                print(f"   📊 Project Profitability Analysis Metrics:")
                print(f"      Revenue: ${proj_revenue:.2f}")
                print(f"      Hours: {proj_hours:.2f}h")
                print(f"      Profit: ${proj_profit:.2f}")
                
            else:
                print("   ❌ Project profitability analysis failed")
                proj_revenue = proj_hours = proj_profit = 0
                
        except Exception as e:
            print(f"   ❌ Error in project profitability analysis: {e}")
            proj_revenue = proj_hours = proj_profit = 0
        
        # Cross-Report Validation
        print(f"\n🔍 CROSS-REPORT VALIDATION:")
        print("=" * 80)
        
        # Revenue consistency
        print(f"📊 REVENUE COMPARISON:")
        print(f"   Organization Dashboard: ${org_revenue:.2f}")
        print(f"   Team Productivity Report: ${team_revenue:.2f}")
        print(f"   Project Profitability Analysis: ${proj_revenue:.2f}")
        
        revenue_values = [v for v in [org_revenue, team_revenue, proj_revenue] if v > 0]
        if revenue_values:
            max_revenue = max(revenue_values)
            min_revenue = min(revenue_values)
            revenue_diff = max_revenue - min_revenue
            
            if revenue_diff < 0.01:
                print(f"   ✅ Revenue consistency: All reports match perfectly")
            elif revenue_diff < max_revenue * 0.02:  # Within 2%
                print(f"   ✅ Revenue consistency: Minor differences (${revenue_diff:.2f}, <2%)")
            else:
                print(f"   ⚠️  Revenue inconsistency: Difference of ${revenue_diff:.2f} ({revenue_diff/max_revenue*100:.1f}%)")
        
        # Hours consistency
        print(f"\n📊 HOURS COMPARISON:")
        print(f"   Organization Dashboard: {org_hours:.2f}h")
        print(f"   Team Productivity Report: {team_hours:.2f}h")
        print(f"   Project Profitability Analysis: {proj_hours:.2f}h")
        
        hours_values = [v for v in [org_hours, team_hours, proj_hours] if v > 0]
        if hours_values:
            max_hours = max(hours_values)
            min_hours = min(hours_values)
            hours_diff = max_hours - min_hours
            
            if hours_diff < 0.1:
                print(f"   ✅ Hours consistency: All reports match perfectly")
            elif hours_diff < max_hours * 0.02:  # Within 2%
                print(f"   ✅ Hours consistency: Minor differences ({hours_diff:.2f}h, <2%)")
            else:
                print(f"   ⚠️  Hours inconsistency: Difference of {hours_diff:.2f}h ({hours_diff/max_hours*100:.1f}%)")
        
        # Profit consistency
        print(f"\n📊 PROFIT COMPARISON:")
        print(f"   Organization Dashboard: ${org_profit:.2f}")
        print(f"   Team Productivity Report: ${team_profit:.2f}")
        print(f"   Project Profitability Analysis: ${proj_profit:.2f}")
        
        profit_values = [v for v in [org_profit, team_profit, proj_profit] if v > 0]
        if profit_values:
            max_profit = max(profit_values)
            min_profit = min(profit_values)
            profit_diff = max_profit - min_profit
            
            if profit_diff < 0.01:
                print(f"   ✅ Profit consistency: All reports match perfectly")
            elif profit_diff < max_profit * 0.02:  # Within 2%
                print(f"   ✅ Profit consistency: Minor differences (${profit_diff:.2f}, <2%)")
            else:
                print(f"   ⚠️  Profit inconsistency: Difference of ${profit_diff:.2f} ({profit_diff/max_profit*100:.1f}%)")
        
        # Overall Assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print("=" * 80)
        
        # Count successful reports
        successful_reports = sum([
            1 if org_revenue > 0 or org_hours > 0 else 0,
            1 if team_revenue > 0 or team_hours > 0 else 0,
            1 if proj_revenue > 0 or proj_hours > 0 else 0
        ])
        
        print(f"📊 Reports Status:")
        print(f"   Organization Dashboard: {'✅ Working' if org_revenue > 0 or org_hours > 0 else '❌ Failed'}")
        print(f"   Team Productivity Report: {'✅ Working' if team_revenue > 0 or team_hours > 0 else '❌ Failed'}")
        print(f"   Project Profitability Analysis: {'✅ Working' if proj_revenue > 0 or proj_hours > 0 else '❌ Failed'}")
        print(f"   Success Rate: {successful_reports}/3 ({successful_reports/3*100:.1f}%)")
        
        # Data consistency assessment
        if successful_reports >= 2:
            all_revenue_consistent = True
            all_hours_consistent = True
            all_profit_consistent = True
            
            if revenue_values and len(revenue_values) >= 2:
                revenue_consistency = (max(revenue_values) - min(revenue_values)) / max(revenue_values)
                all_revenue_consistent = revenue_consistency < 0.05  # Within 5%
            
            if hours_values and len(hours_values) >= 2:
                hours_consistency = (max(hours_values) - min(hours_values)) / max(hours_values)
                all_hours_consistent = hours_consistency < 0.05  # Within 5%
            
            if profit_values and len(profit_values) >= 2:
                profit_consistency = (max(profit_values) - min(profit_values)) / max(profit_values)
                all_profit_consistent = profit_consistency < 0.05  # Within 5%
            
            consistency_score = sum([all_revenue_consistent, all_hours_consistent, all_profit_consistent]) / 3
            
            print(f"\n📊 Data Consistency:")
            print(f"   Revenue Consistency: {'✅' if all_revenue_consistent else '⚠️ '} {(1-revenue_consistency)*100:.1f}%" if revenue_values and len(revenue_values) >= 2 else "N/A")
            print(f"   Hours Consistency: {'✅' if all_hours_consistent else '⚠️ '} {(1-hours_consistency)*100:.1f}%" if hours_values and len(hours_values) >= 2 else "N/A")
            print(f"   Profit Consistency: {'✅' if all_profit_consistent else '⚠️ '} {(1-profit_consistency)*100:.1f}%" if profit_values and len(profit_values) >= 2 else "N/A")
            print(f"   Overall Consistency: {consistency_score*100:.1f}%")
            
            if consistency_score >= 0.9:
                print(f"   🎉 EXCELLENT: All reports are highly consistent!")
            elif consistency_score >= 0.7:
                print(f"   ✅ GOOD: Reports are mostly consistent")
            else:
                print(f"   ⚠️  NEEDS ATTENTION: Some inconsistencies detected")
        
        # Compare with expected values
        if proj_revenue > 0:  # Use project profitability as the reference
            print(f"\n🎯 COMPARISON WITH EXPECTED VALUES:")
            print(f"   Expected Revenue: $43,677.66")
            print(f"   Actual Revenue (Project Analysis): ${proj_revenue:.2f}")
            print(f"   Revenue Accuracy: {(proj_revenue/43677.66)*100:.1f}%")
            
            if proj_profit > 0:
                print(f"   Expected Profit: $22,587.55")
                print(f"   Actual Profit (Project Analysis): ${proj_profit:.2f}")
                print(f"   Profit Accuracy: {(proj_profit/22587.55)*100:.1f}%")
        
        print(f"\n🎯 COMPREHENSIVE TEST SUMMARY:")
        print(f"   • Tested all three main reports")
        print(f"   • Validated cross-report consistency")
        print(f"   • Compared with expected business metrics")
        print(f"   • Overall system health: {successful_reports}/3 reports working")
        print(f"   • Data consistency: {consistency_score*100:.1f}%" if 'consistency_score' in locals() else "N/A")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_all_reports_consistency())
