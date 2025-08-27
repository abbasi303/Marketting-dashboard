"""
Data transformation service to enhance marketing data with calculated metrics
"""

import json
import os
import pandas as pd
import numpy as np
from flask import current_app

def enhance_marketing_data():
    """
    Enhance the marketing data by combining different data sources
    and calculating missing metrics
    """
    data_path = os.path.join(current_app.instance_path, 'data', 'processed_data.json')
    
    if not os.path.exists(data_path):
        return None
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        # Enhance channel performance data
        if 'channel_performance' in data and 'cac' in data:
            enhanced_channels = enhance_channel_data(data['channel_performance'], data['cac'])
            data['channel_performance'] = enhanced_channels
        
        # Enhance campaign performance data
        if 'campaign_performance' in data and 'cac' in data:
            enhanced_campaigns = enhance_campaign_data(data['campaign_performance'], data['cac'])
            data['campaign_performance'] = enhanced_campaigns
        
        # Create enhanced CAC table
        if 'cac' in data:
            enhanced_cac = enhance_cac_data(data['cac'])
            data['enhanced_cac'] = enhanced_cac
        
        return data
        
    except Exception as e:
        current_app.logger.error(f"Error enhancing marketing data: {str(e)}")
        return None

def enhance_channel_data(channel_performance, cac_data):
    """
    Enhance channel performance data with CAC information
    """
    enhanced_channels = []
    
    # Create a lookup dictionary for CAC data by channel
    cac_by_channel = {}
    for cac_entry in cac_data:
        channel = cac_entry.get('channel', 'Unknown')
        if channel not in cac_by_channel:
            cac_by_channel[channel] = []
        cac_by_channel[channel].append(cac_entry)
    
    for channel_entry in channel_performance:
        channel_name = channel_entry.get('channel', 'Unknown')
        enhanced_entry = channel_entry.copy()
        
        # Calculate metrics from existing data
        views = channel_entry.get('views', 0)
        signups = channel_entry.get('signups', 0)
        purchases = channel_entry.get('purchases', 0)
        signup_rate = channel_entry.get('signup_rate', 0)
        purchase_rate = channel_entry.get('purchase_rate', 0)
        
        # Add calculated metrics
        enhanced_entry['conversion_rate'] = purchase_rate  # Final conversion rate
        enhanced_entry['roi'] = purchase_rate * 2.5 if purchase_rate > 0 else 0  # Estimated ROI
        
        # Get CAC information for this channel
        if channel_name in cac_by_channel:
            channel_cac_entries = cac_by_channel[channel_name]
            
            # Calculate average CAC for this channel
            total_cost = sum(entry.get('total_cost', 0) for entry in channel_cac_entries)
            total_acquisitions = sum(entry.get('acquisitions', 0) for entry in channel_cac_entries)
            
            if total_acquisitions > 0:
                enhanced_entry['acquisition_cost'] = total_cost / total_acquisitions
            else:
                # Estimate based on views if no acquisitions
                enhanced_entry['acquisition_cost'] = (views * 0.75) / max(purchases, 1)
        else:
            # Estimate CAC if no specific data available
            enhanced_entry['acquisition_cost'] = (views * 0.50) / max(purchases, 1)
        
        # Add additional calculated metrics
        enhanced_entry['cost_per_click'] = (views * 0.25) / max(views, 1)
        enhanced_entry['revenue'] = purchases * 75  # Estimated revenue per purchase
        enhanced_entry['profit'] = enhanced_entry['revenue'] - (enhanced_entry['acquisition_cost'] * purchases)
        
        enhanced_channels.append(enhanced_entry)
    
    return enhanced_channels

def enhance_campaign_data(campaign_performance, cac_data):
    """
    Enhance campaign performance data with CAC information
    """
    enhanced_campaigns = []
    
    # Create a lookup dictionary for CAC data by campaign
    cac_by_campaign = {}
    for cac_entry in cac_data:
        campaign = cac_entry.get('campaign', 'Unknown')
        if campaign not in cac_by_campaign:
            cac_by_campaign[campaign] = []
        cac_by_campaign[campaign].append(cac_entry)
    
    for campaign_entry in campaign_performance:
        campaign_name = campaign_entry.get('campaign', 'Unknown')
        enhanced_entry = campaign_entry.copy()
        
        # Calculate metrics from existing data
        views = campaign_entry.get('views', 0)
        signups = campaign_entry.get('signups', 0)
        purchases = campaign_entry.get('purchases', 0)
        signup_rate = campaign_entry.get('signup_rate', 0)
        purchase_rate = campaign_entry.get('purchase_rate', 0)
        
        # Add calculated metrics
        enhanced_entry['conversion_rate'] = purchase_rate
        enhanced_entry['roi'] = purchase_rate * 3.0 if purchase_rate > 0 else 0
        
        # Get CAC information for this campaign
        if campaign_name in cac_by_campaign:
            campaign_cac_entries = cac_by_campaign[campaign_name]
            
            # Calculate totals for this campaign
            total_cost = sum(entry.get('total_cost', 0) for entry in campaign_cac_entries)
            total_acquisitions = sum(entry.get('acquisitions', 0) for entry in campaign_cac_entries)
            total_clicks = sum(entry.get('clicks', 0) for entry in campaign_cac_entries)
            total_impressions = sum(entry.get('impressions', 0) for entry in campaign_cac_entries)
            
            enhanced_entry['cost'] = total_cost
            enhanced_entry['clicks'] = total_clicks
            enhanced_entry['impressions'] = total_impressions
            
            if total_acquisitions > 0:
                enhanced_entry['acquisition_cost'] = total_cost / total_acquisitions
            else:
                enhanced_entry['acquisition_cost'] = total_cost / max(purchases, 1)
        else:
            # Estimate values if no CAC data available
            enhanced_entry['cost'] = views * 0.60
            enhanced_entry['acquisition_cost'] = enhanced_entry['cost'] / max(purchases, 1)
            enhanced_entry['clicks'] = views
            enhanced_entry['impressions'] = views * 2
        
        # Add additional metrics
        enhanced_entry['revenue'] = purchases * 85  # Estimated revenue per purchase
        enhanced_entry['profit'] = enhanced_entry['revenue'] - enhanced_entry['cost']
        enhanced_entry['roas'] = enhanced_entry['revenue'] / enhanced_entry['cost'] if enhanced_entry['cost'] > 0 else 0
        
        enhanced_campaigns.append(enhanced_entry)
    
    return enhanced_campaigns

def enhance_cac_data(cac_data):
    """
    Create an enhanced CAC table with better formatting and additional metrics
    """
    enhanced_cac = []
    
    for cac_entry in cac_data:
        enhanced_entry = cac_entry.copy()
        
        # Handle null/zero values
        acquisitions = cac_entry.get('acquisitions', 0)
        total_cost = cac_entry.get('total_cost', 0)
        clicks = cac_entry.get('clicks', 0)
        impressions = cac_entry.get('impressions', 0)
        
        # Calculate or estimate missing values
        if acquisitions == 0 and clicks > 0:
            # Estimate acquisitions from clicks using average conversion rate
            enhanced_entry['acquisitions'] = max(1, int(clicks * 0.15))  # 15% estimated conversion rate
            acquisitions = enhanced_entry['acquisitions']
        
        if total_cost == 0 and impressions > 0:
            # Estimate cost based on impressions
            enhanced_entry['total_cost'] = impressions * 0.05  # $0.05 per impression
            total_cost = enhanced_entry['total_cost']
        
        # Calculate CAC
        if acquisitions > 0 and total_cost > 0:
            enhanced_entry['cac'] = total_cost / acquisitions
        else:
            enhanced_entry['cac'] = 0
        
        # Calculate additional metrics
        if impressions > 0 and clicks > 0:
            enhanced_entry['ctr'] = (clicks / impressions) * 100  # Click-through rate
        else:
            enhanced_entry['ctr'] = 0
        
        if clicks > 0 and acquisitions > 0:
            enhanced_entry['conversion_rate'] = (acquisitions / clicks) * 100
        else:
            enhanced_entry['conversion_rate'] = 0
        
        # Estimate ROI
        estimated_revenue = acquisitions * 75  # $75 average revenue per acquisition
        if total_cost > 0:
            enhanced_entry['roi'] = ((estimated_revenue - total_cost) / total_cost) * 100
        else:
            enhanced_entry['roi'] = 0
        
        enhanced_cac.append(enhanced_entry)
    
    return enhanced_cac

def get_enhanced_data():
    """
    Get enhanced marketing data, generating it if not already cached
    """
    try:
        enhanced_data = enhance_marketing_data()
        return enhanced_data
    except Exception as e:
        current_app.logger.error(f"Error getting enhanced data: {str(e)}")
        return None
