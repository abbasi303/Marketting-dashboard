"""
Data Consistency Checker
Diagnoses inconsistencies between dashboard data and analytics data
"""

import json
import os
from flask import Flask, current_app
from app import create_app
from app.services.data_enhancement import get_enhanced_data
from app.services.analytics_service import generate_analytics_report

def check_data_consistency():
    """Check for inconsistencies between different data sources"""
    
    print("=== Data Consistency Check ===\n")
    
    # Load raw processed data
    raw_data_path = os.path.join(current_app.instance_path, 'data', 'processed_data.json')
    if os.path.exists(raw_data_path):
        with open(raw_data_path, 'r') as f:
            raw_data = json.load(f)
        print("✓ Raw processed data loaded")
        print(f"Raw data sections: {list(raw_data.keys())}\n")
    else:
        print("✗ No raw processed data found")
        return
    
    # Load enhanced data
    enhanced_data = get_enhanced_data()
    if enhanced_data:
        print("✓ Enhanced data loaded")
        print(f"Enhanced data sections: {list(enhanced_data.keys())}\n")
    else:
        print("✗ Enhanced data failed to load")
        return
    
    # Generate analytics report
    analytics_report = generate_analytics_report()
    print("✓ Analytics report generated")
    print(f"Analytics report sections: {list(analytics_report.keys())}\n")
    
    # Check funnel data consistency
    print("=== Funnel Data Analysis ===")
    if 'funnel' in raw_data:
        funnel = raw_data['funnel']
        print(f"Funnel data: {funnel}")
        
        if 'summary' in analytics_report and 'funnel' in analytics_report['summary']:
            funnel_analysis = analytics_report['summary']['funnel']
            print(f"Funnel analysis: {funnel_analysis}")
        else:
            print("✗ No funnel analysis in analytics report")
    print()
    
    # Check campaign data consistency
    print("=== Campaign Data Analysis ===")
    if 'campaign_performance' in raw_data:
        campaigns = raw_data['campaign_performance']
        print(f"Raw campaigns count: {len(campaigns)}")
        if campaigns:
            print(f"Raw campaign fields: {list(campaigns[0].keys())}")
        
        if 'campaign_performance' in enhanced_data:
            enhanced_campaigns = enhanced_data['campaign_performance']
            print(f"Enhanced campaigns count: {len(enhanced_campaigns)}")
            if enhanced_campaigns:
                print(f"Enhanced campaign fields: {list(enhanced_campaigns[0].keys())}")
        
        if 'summary' in analytics_report and 'campaigns' in analytics_report['summary']:
            campaign_analysis = analytics_report['summary']['campaigns']
            print(f"Campaign analysis: {campaign_analysis}")
        else:
            print("✗ No campaign analysis in analytics report")
    print()
    
    # Check channel data consistency
    print("=== Channel Data Analysis ===")
    if 'channel_performance' in raw_data:
        channels = raw_data['channel_performance']
        print(f"Raw channels count: {len(channels)}")
        if channels:
            print(f"Raw channel fields: {list(channels[0].keys())}")
        
        if 'channel_performance' in enhanced_data:
            enhanced_channels = enhanced_data['channel_performance']
            print(f"Enhanced channels count: {len(enhanced_channels)}")
            if enhanced_channels:
                print(f"Enhanced channel fields: {list(enhanced_channels[0].keys())}")
        
        if 'summary' in analytics_report and 'channels' in analytics_report['summary']:
            channel_analysis = analytics_report['summary']['channels']
            print(f"Channel analysis: {channel_analysis}")
        else:
            print("✗ No channel analysis in analytics report")
    print()
    
    # Check CAC data consistency  
    print("=== CAC Data Analysis ===")
    if 'cac' in raw_data:
        cac_data = raw_data['cac']
        print(f"Raw CAC entries: {len(cac_data)}")
        if cac_data:
            print(f"Raw CAC fields: {list(cac_data[0].keys())}")
            # Show first entry with data
            for entry in cac_data:
                if entry.get('total_cost', 0) > 0 or entry.get('acquisitions', 0) > 0:
                    print(f"Sample CAC entry: {entry}")
                    break
        
        if 'enhanced_cac' in enhanced_data:
            enhanced_cac = enhanced_data['enhanced_cac']
            print(f"Enhanced CAC entries: {len(enhanced_cac)}")
            if enhanced_cac:
                print(f"Enhanced CAC fields: {list(enhanced_cac[0].keys())}")
                # Show first entry
                print(f"Sample enhanced CAC entry: {enhanced_cac[0]}")
    print()
    
    # Check for missing data patterns
    print("=== Data Issues Analysis ===")
    
    # Check for zeros in CAC data
    if 'cac' in raw_data:
        zero_cost_entries = sum(1 for entry in raw_data['cac'] if entry.get('total_cost', 0) == 0)
        zero_acquisitions = sum(1 for entry in raw_data['cac'] if entry.get('acquisitions', 0) == 0)
        print(f"CAC entries with zero cost: {zero_cost_entries}/{len(raw_data['cac'])}")
        print(f"CAC entries with zero acquisitions: {zero_acquisitions}/{len(raw_data['cac'])}")
    
    # Check analytics report for errors
    if 'error' in analytics_report:
        print(f"✗ Analytics report error: {analytics_report['error']}")
    
    if 'insights' in analytics_report:
        print(f"Analytics insights count: {len(analytics_report['insights'])}")
    
    if 'recommendations' in analytics_report:
        print(f"Analytics recommendations count: {len(analytics_report['recommendations'])}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        check_data_consistency()
