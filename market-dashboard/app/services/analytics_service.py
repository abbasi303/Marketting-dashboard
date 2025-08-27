# Marketing Analytics Report Generator

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from flask import current_app
from app.services.data_enhancement import get_enhanced_data

def generate_analytics_report():
    """Generate a comprehensive marketing analytics report"""
    report = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {},
        'insights': [],
        'recommendations': []
    }
    
    # Load the enhanced data
    data = get_enhanced_data()
    if not data:
        report['error'] = 'No processed data available'
        return report
    
    try:
        # Process funnel data
        if 'funnel' in data:
            funnel = data['funnel']
            report['summary']['funnel'] = analyze_funnel(funnel)
        
        # Process conversion rates data
        if 'conversion_rates' in data:
            conversion_rates = data['conversion_rates']
            report['summary']['conversion_rates'] = analyze_conversion_rates(conversion_rates)
        
        # Process campaign performance data
        if 'campaign_performance' in data:
            campaigns = data['campaign_performance']
            campaign_analysis = analyze_campaigns(campaigns)
            report['summary']['campaigns'] = campaign_analysis['summary']
            report['insights'].extend(campaign_analysis['insights'])
            report['recommendations'].extend(campaign_analysis['recommendations'])
        
        # Process channel performance data
        if 'channel_performance' in data:
            channels = data['channel_performance']
            channel_analysis = analyze_channels(channels)
            report['summary']['channels'] = channel_analysis['summary']
            report['insights'].extend(channel_analysis['insights'])
            report['recommendations'].extend(channel_analysis['recommendations'])
        
        # Add overall insights
        add_overall_insights(report, data)
        
    except Exception as e:
        report['error'] = f'Error analyzing data: {str(e)}'
    
    return report

def analyze_funnel(funnel):
    """Analyze the marketing funnel data"""
    summary = {
        'stages': [],
        'drop_offs': [],
        'conversion_rates': []
    }
    
    # Check for campaign data format
    if 'impressions' in funnel:
        impressions = funnel.get('impressions', 0)
        clicks = funnel.get('clicks', 0)
        conversions = funnel.get('conversions', 0)
        
        # Add stages
        summary['stages'] = [
            {'name': 'Impressions', 'value': impressions},
            {'name': 'Clicks', 'value': clicks},
            {'name': 'Conversions', 'value': conversions}
        ]
        
        # Calculate drop-offs
        if impressions > 0:
            summary['drop_offs'].append({
                'from': 'Impressions',
                'to': 'Clicks',
                'absolute': impressions - clicks,
                'percent': (1 - clicks / impressions) * 100 if impressions > 0 else 0
            })
        
        if clicks > 0:
            summary['drop_offs'].append({
                'from': 'Clicks',
                'to': 'Conversions',
                'absolute': clicks - conversions,
                'percent': (1 - conversions / clicks) * 100 if clicks > 0 else 0
            })
        
        # Calculate conversion rates
        summary['conversion_rates'] = [
            {'name': 'Click-Through Rate', 'value': (clicks / impressions * 100) if impressions > 0 else 0},
            {'name': 'Conversion Rate', 'value': (conversions / clicks * 100) if clicks > 0 else 0},
            {'name': 'Overall Conversion Rate', 'value': (conversions / impressions * 100) if impressions > 0 else 0}
        ]
    
    # Check for event data format
    elif 'page_view' in funnel:
        page_views = funnel.get('page_view', 0)
        signups = funnel.get('signup', 0)
        purchases = funnel.get('purchase', 0)
        
        # Add stages
        summary['stages'] = [
            {'name': 'Page Views', 'value': page_views},
            {'name': 'Signups', 'value': signups},
            {'name': 'Purchases', 'value': purchases}
        ]
        
        # Calculate drop-offs
        if page_views > 0:
            summary['drop_offs'].append({
                'from': 'Page Views',
                'to': 'Signups',
                'absolute': page_views - signups,
                'percent': (1 - signups / page_views) * 100 if page_views > 0 else 0
            })
        
        if signups > 0:
            summary['drop_offs'].append({
                'from': 'Signups',
                'to': 'Purchases',
                'absolute': signups - purchases,
                'percent': (1 - purchases / signups) * 100 if signups > 0 else 0
            })
        
        # Calculate conversion rates
        summary['conversion_rates'] = [
            {'name': 'Signup Rate', 'value': (signups / page_views * 100) if page_views > 0 else 0},
            {'name': 'Purchase Rate', 'value': (purchases / signups * 100) if signups > 0 else 0},
            {'name': 'Overall Conversion Rate', 'value': (purchases / page_views * 100) if page_views > 0 else 0}
        ]
    
    return summary

def analyze_conversion_rates(conversion_rates):
    """Analyze the conversion rates data"""
    summary = {'metrics': []}
    
    # Check for campaign data format
    if 'click_through_rate' in conversion_rates:
        ctr = conversion_rates.get('click_through_rate', 0)
        cr = conversion_rates.get('conversion_rate', 0)
        roi = conversion_rates.get('roi', 0)
        
        summary['metrics'] = [
            {'name': 'Click-Through Rate', 'value': ctr, 'benchmark': 2.0, 'status': 'good' if ctr > 2.0 else 'needs_improvement'},
            {'name': 'Conversion Rate', 'value': cr, 'benchmark': 3.0, 'status': 'good' if cr > 3.0 else 'needs_improvement'},
            {'name': 'ROI', 'value': roi, 'benchmark': 100.0, 'status': 'good' if roi > 100.0 else 'needs_improvement'}
        ]
    
    # Check for event data format
    elif 'signup_rate' in conversion_rates:
        signup_rate = conversion_rates.get('signup_rate', 0)
        purchase_rate = conversion_rates.get('purchase_rate', 0)
        overall_conversion = conversion_rates.get('overall_conversion', 0)
        
        summary['metrics'] = [
            {'name': 'Signup Rate', 'value': signup_rate, 'benchmark': 10.0, 'status': 'good' if signup_rate > 10.0 else 'needs_improvement'},
            {'name': 'Purchase Rate', 'value': purchase_rate, 'benchmark': 25.0, 'status': 'good' if purchase_rate > 25.0 else 'needs_improvement'},
            {'name': 'Overall Conversion', 'value': overall_conversion, 'benchmark': 2.5, 'status': 'good' if overall_conversion > 2.5 else 'needs_improvement'}
        ]
    
    return summary

def analyze_campaigns(campaigns):
    """Analyze campaign performance data"""
    result = {
        'summary': {},
        'insights': [],
        'recommendations': []
    }
    
    if not campaigns or len(campaigns) == 0:
        result['summary'] = {'error': 'No campaign data available'}
        return result
    
    # Convert to pandas DataFrame for easier analysis
    try:
        df = pd.DataFrame(campaigns)
        
        # Current data has: campaign, views, signups, purchases, signup_rate, purchase_rate
        # Need to calculate ROI, cost, revenue
        if 'campaign' not in df.columns and 'campaign_name' in df.columns:
            df['campaign'] = df['campaign_name']
        elif 'campaign' not in df.columns and 'campaign_type' in df.columns:
            df['campaign'] = df['campaign_type']
        
        df = df.fillna({
            'purchase_rate': 0,
            'signup_rate': 0,
            'views': 0,
            'signups': 0,
            'purchases': 0
        })
        
        # Calculate derived metrics
        df['roi'] = df['purchase_rate'] * 3  # Simplified ROI calculation
        df['cost'] = df['views'] * 0.50  # Estimated cost based on views
        df['revenue'] = df['purchases'] * 50  # Estimated revenue per purchase
        df['conversion_rate'] = df['purchase_rate']  # Purchase rate is the final conversion
        
        # Calculate basic stats
        result['summary'] = {
            'count': len(df),
            'total_cost': df['cost'].sum(),
            'total_revenue': df['revenue'].sum(),
            'average_roi': df['roi'].mean(),
            'average_conversion_rate': df['conversion_rate'].mean()
        }
        
        # Identify top and bottom performers
        if len(df) > 0:
            top_campaigns = df.nlargest(3, 'roi')
            bottom_campaigns = df.nsmallest(3, 'roi')
            
            result['summary']['top_campaigns'] = top_campaigns['campaign'].tolist()
            result['summary']['bottom_campaigns'] = bottom_campaigns['campaign'].tolist()
            
            # Generate insights
            for _, campaign in top_campaigns.iterrows():
                if campaign['roi'] > 150:
                    result['insights'].append({
                        'type': 'success',
                        'message': f"Campaign '{campaign['campaign']}' is performing exceptionally well with {campaign['roi']:.1f}% ROI."
                    })
                    result['recommendations'].append({
                        'priority': 'high',
                        'message': f"Consider increasing budget for '{campaign['campaign']}' to capitalize on its strong performance."
                    })
            
            for _, campaign in bottom_campaigns.iterrows():
                if campaign['roi'] < 100:
                    result['insights'].append({
                        'type': 'warning',
                        'message': f"Campaign '{campaign['campaign']}' is underperforming with only {campaign['roi']:.1f}% ROI."
                    })
                    result['recommendations'].append({
                        'priority': 'high',
                        'message': f"Review and optimize '{campaign['campaign']}' campaign, or consider reallocating budget to better-performing campaigns."
                    })
        
    except Exception as e:
        result['summary'] = {'error': f'Error analyzing campaign data: {str(e)}'}
    
    return result

def analyze_channels(channels):
    """Analyze channel performance data"""
    result = {
        'summary': {},
        'insights': [],
        'recommendations': []
    }
    
    if not channels or len(channels) == 0:
        result['summary'] = {'error': 'No channel data available'}
        return result
    
    # Convert to pandas DataFrame for easier analysis
    try:
        df = pd.DataFrame(channels)
        
        # Calculate additional metrics from the existing data
        # Current data has: channel, views, signups, purchases, signup_rate, purchase_rate
        df = df.fillna({
            'channel': 'Unknown',
            'signup_rate': 0,
            'purchase_rate': 0,
            'views': 0,
            'signups': 0,
            'purchases': 0
        })
        
        # Calculate derived metrics
        df['conversion_rate'] = df['purchase_rate']  # Purchase rate is the final conversion
        df['roi'] = df['purchase_rate'] * 2  # Simplified ROI calculation
        df['acquisition_cost'] = np.where(df['purchases'] > 0, 
                                        (df['views'] * 0.50) / df['purchases'], 
                                        df['views'] * 0.50)  # Estimated cost per acquisition
        
        # Calculate basic stats
        result['summary'] = {
            'count': len(df),
            'average_roi': df['roi'].mean(),
            'average_conversion_rate': df['conversion_rate'].mean(),
            'average_acquisition_cost': df['acquisition_cost'].mean()
        }
        
        # Identify most efficient and least efficient channels
        if len(df) > 0:
            top_roi_channels = df.nlargest(2, 'roi')
            bottom_roi_channels = df.nsmallest(2, 'roi')
            
            result['summary']['top_roi_channels'] = top_roi_channels['channel'].tolist()
            result['summary']['bottom_roi_channels'] = bottom_roi_channels['channel'].tolist()
            
            lowest_cac_channels = df.nsmallest(2, 'acquisition_cost')
            highest_cac_channels = df.nlargest(2, 'acquisition_cost')
            
            result['summary']['lowest_cac_channels'] = lowest_cac_channels['channel'].tolist()
            result['summary']['highest_cac_channels'] = highest_cac_channels['channel'].tolist()
            
            # Calculate efficiency (conversion rate / cost)
            df['efficiency'] = df.apply(
                lambda x: x['conversion_rate'] / x['acquisition_cost'] if x['acquisition_cost'] > 0 else 0, 
                axis=1
            )
            
            most_efficient_channels = df.nlargest(2, 'efficiency')
            result['summary']['most_efficient_channels'] = most_efficient_channels['channel'].tolist()
            
            # Generate insights
            for _, channel in most_efficient_channels.iterrows():
                result['insights'].append({
                    'type': 'success',
                    'message': f"'{channel['channel']}' is your most efficient channel with {channel['conversion_rate']:.1f}% conversion rate at ${channel['acquisition_cost']:.2f} cost per acquisition."
                })
                result['recommendations'].append({
                    'priority': 'high',
                    'message': f"Increase investment in '{channel['channel']}' to leverage its efficiency."
                })
            
            for _, channel in highest_cac_channels.iterrows():
                if channel['acquisition_cost'] > result['summary']['average_acquisition_cost'] * 1.5:
                    result['insights'].append({
                        'type': 'warning',
                        'message': f"'{channel['channel']}' has an unusually high acquisition cost (${channel['acquisition_cost']:.2f})."
                    })
                    result['recommendations'].append({
                        'priority': 'medium',
                        'message': f"Review and optimize spending in '{channel['channel']}' to improve efficiency."
                    })
        
    except Exception as e:
        result['summary'] = {'error': f'Error analyzing channel data: {str(e)}'}
    
    return result

def add_overall_insights(report, data):
    """Add overall insights across all data points"""
    
    # Add cross-channel insights
    if 'summary' in report and 'channels' in report['summary'] and 'campaigns' in report['summary']:
        # Identify misalignments between top channels and campaign focus
        if ('top_roi_channels' in report['summary']['channels'] and 
            'top_campaigns' in report['summary']['campaigns']):
            
            report['insights'].append({
                'type': 'insight',
                'message': "Cross-analysis of campaigns and channels reveals opportunities for better alignment of resources."
            })
            
            report['recommendations'].append({
                'priority': 'medium',
                'message': "Consider creating channel-specific campaigns for your top-performing channels to maximize ROI."
            })
    
    # Add funnel optimization insights
    if 'summary' in report and 'funnel' in report['summary']:
        funnel_summary = report['summary']['funnel']
        
        # Check for high drop-off rates
        if 'drop_offs' in funnel_summary and len(funnel_summary['drop_offs']) > 0:
            highest_drop_off = max(funnel_summary['drop_offs'], key=lambda x: x['percent'])
            
            if highest_drop_off['percent'] > 70:
                report['insights'].append({
                    'type': 'warning',
                    'message': f"There's a significant drop-off ({highest_drop_off['percent']:.1f}%) between {highest_drop_off['from']} and {highest_drop_off['to']}."
                })
                
                report['recommendations'].append({
                    'priority': 'high',
                    'message': f"Focus on optimizing the transition from {highest_drop_off['from']} to {highest_drop_off['to']} to improve overall conversion."
                })
    
    # Add overall budget allocation recommendations
    if 'channel_performance' in data and 'campaign_performance' in data:
        report['recommendations'].append({
            'priority': 'high',
            'message': "Consider reallocating budget from low-performing channels and campaigns to high-performing ones to improve overall marketing ROI."
        })
    
    # Add recommendation for A/B testing
    report['recommendations'].append({
        'priority': 'medium',
        'message': "Implement A/B testing for key marketing elements to continuously improve performance."
    })
    
    return report
