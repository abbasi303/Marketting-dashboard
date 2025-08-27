import os
import pandas as pd
import json
from flask import current_app


def validate_csv(file_path, file_type='campaign'):
    """
    Validate the CSV file structure
    
    Args:
        file_path (str): Path to the CSV file
        file_type (str): Type of data - 'campaign' or 'costs'
    
    Returns:
        dict: Validation result with 'valid' flag and potential 'errors'
    """
    try:
        df = pd.read_csv(file_path)
        errors = []
        
        if file_type == 'campaign':
            # Check required columns for marketing campaign data
            required_columns = [
                'Campaign_ID', 'Company', 'Campaign_Type', 'Channel_Used',
                'Conversion_Rate', 'Acquisition_Cost', 'ROI', 'Clicks',
                'Impressions', 'Date'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"Missing required column: {col}")
        
        elif file_type == 'events':
            # For backward compatibility
            required_columns = ['user_id', 'event_type', 'campaign', 'channel', 'timestamp']
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"Missing required column: {col}")
            
            # Check event types
            if 'event_type' in df.columns:
                valid_event_types = ['page_view', 'signup', 'purchase']
                invalid_events = df[~df['event_type'].isin(valid_event_types)]['event_type'].unique()
                if len(invalid_events) > 0:
                    errors.append(f"Invalid event types found: {', '.join(invalid_events)}")
        
        elif file_type == 'costs':
            # Check required columns for cost data
            required_columns = ['campaign', 'channel', 'cpc', 'cpm']
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"Missing required column: {col}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    except Exception as e:
        return {
            'valid': False,
            'errors': [f"Error reading CSV file: {str(e)}"]
        }


def process_marketing_data(file_path, file_type='campaign'):
    """
    Process marketing data from CSV
    
    Args:
        file_path (str): Path to the CSV file
        file_type (str): Type of data - 'campaign' or 'events'
    
    Returns:
        dict: Processed metrics and KPIs
    """
    try:
        # Ensure required directories exist
        if not os.path.exists(os.path.join(current_app.instance_path, 'data')):
            os.makedirs(os.path.join(current_app.instance_path, 'data'), exist_ok=True)
            print(f"Created directory: {os.path.join(current_app.instance_path, 'data')}")
            
        # Determine the type of data we're processing
        if file_type == 'campaign':
            result = process_marketing_campaign_data(file_path)
            # Verify that the data was processed and saved correctly
            data_path = os.path.join(current_app.instance_path, 'data', 'processed_data.json')
            if os.path.exists(data_path):
                print(f"Successfully created processed data file at {data_path}")
                # Read back the file to verify its structure
                try:
                    with open(data_path, 'r') as f:
                        data = json.load(f)
                    print(f"Processed data sections: {list(data.keys())}")
                except Exception as e:
                    print(f"Error verifying processed data file: {str(e)}")
            else:
                print(f"Warning: Processed data file not created at {data_path}")
            
            return result
        else:  # Original events data format
            return process_marketing_events_data(file_path)
    except Exception as e:
        print(f"Error in process_marketing_data: {str(e)}")
        return {
            'error': str(e)
        }

def process_marketing_campaign_data(file_path):
    """
    Process marketing campaign data from CSV
    
    Args:
        file_path (str): Path to the marketing campaign CSV file
    
    Returns:
        dict: Processed metrics and KPIs
    """
    try:
        # Read campaign data with optimizations
        # Use chunksize for large files, but we'll start by seeing if we can read the whole file
        try:
            # Check file size
            import os
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
            
            if file_size > 50:  # If file is larger than 50MB, use chunking
                print(f"Large file detected ({file_size:.2f} MB). Processing in chunks...")
                # Process large file in chunks
                return process_large_campaign_file(file_path)
            else:
                # Read the entire file at once for smaller files
                df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error checking file size: {str(e)}. Falling back to chunked processing.")
            return process_large_campaign_file(file_path)
        
        # Clean and convert data
        # Use more efficient conversion
        df['Acquisition_Cost'] = pd.to_numeric(
            df['Acquisition_Cost'].str.replace('$', '').str.replace(',', ''),
            errors='coerce'
        )
        
        # Convert date efficiently (only if needed for analysis)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Basic data validation
        # We skip full validation for large files to improve performance
        # validate_csv(file_path, 'campaign')
        
        # Calculate metrics efficiently using vectorized operations
        total_clicks = df['Clicks'].sum()
        total_impressions = df['Impressions'].sum()
        
        # Get summary stats in one go to avoid repeated calculations
        conversion_stats = df['Conversion_Rate'].agg(['mean', 'median', 'min', 'max'])
        roi_stats = df['ROI'].agg(['mean', 'median', 'min', 'max'])
        
        # Funnel metrics - convert to int once, not repeatedly
        funnel = {
            'impressions': int(total_impressions),
            'clicks': int(total_clicks),
            'conversions': int(total_clicks * conversion_stats['mean'])
        }
        
        # Conversion rates
        conversion_rates = {
            'click_through_rate': round((total_clicks / total_impressions) * 100 if total_impressions > 0 else 0, 2),
            'conversion_rate': round(conversion_stats['mean'] * 100, 2),
            'roi': round(roi_stats['mean'], 2)
        }
        
        # For performance, limit to top companies rather than processing all
        # Get top 10 companies by ROI
        top_companies = df.groupby('Company').agg({
            'Impressions': 'sum',
            'Clicks': 'sum',
            'Conversion_Rate': 'mean',
            'ROI': 'mean',
            'Acquisition_Cost': 'mean'
        }).nlargest(10, 'ROI')
        
        # Campaign performance for top companies
        campaign_performance = []
        for company, row in top_companies.iterrows():
            campaign_performance.append({
                'campaign': company,
                'impressions': int(row['Impressions']),
                'clicks': int(row['Clicks']),
                'conversion_rate': round(row['Conversion_Rate'] * 100, 2),
                'roi': round(row['ROI'], 2),
                'acquisition_cost': round(row['Acquisition_Cost'], 2)
            })
        
        # Channel performance - use groupby for efficiency
        channel_agg = df.groupby('Channel_Used').agg({
            'Impressions': 'sum',
            'Clicks': 'sum',
            'Conversion_Rate': 'mean',
            'ROI': 'mean',
            'Acquisition_Cost': 'mean'
        })
        
        channel_performance = []
        for channel, row in channel_agg.iterrows():
            channel_performance.append({
                'channel': channel,
                'impressions': int(row['Impressions']),
                'clicks': int(row['Clicks']),
                'conversion_rate': round(row['Conversion_Rate'] * 100, 2),
                'roi': round(row['ROI'], 2),
                'acquisition_cost': round(row['Acquisition_Cost'], 2)
            })
        
        # Sort by conversion rate
        channel_performance = sorted(
            channel_performance, 
            key=lambda x: x['conversion_rate'], 
            reverse=True
        )
        
        # Campaign type performance - use groupby
        campaign_type_agg = df.groupby('Campaign_Type').agg({
            'Impressions': 'sum',
            'Clicks': 'sum',
            'Conversion_Rate': 'mean',
            'ROI': 'mean',
            'Acquisition_Cost': 'mean'
        })
        
        campaign_type_performance = []
        for campaign_type, row in campaign_type_agg.iterrows():
            campaign_type_performance.append({
                'type': campaign_type,
                'impressions': int(row['Impressions']),
                'clicks': int(row['Clicks']),
                'conversion_rate': round(row['Conversion_Rate'] * 100, 2),
                'roi': round(row['ROI'], 2),
                'acquisition_cost': round(row['Acquisition_Cost'], 2)
            })
        
        # Target audience performance (if available)
        audience_performance = []
        if 'Target_Audience' in df.columns:
            audience_agg = df.groupby('Target_Audience').agg({
                'Impressions': 'sum',
                'Clicks': 'sum',
                'Conversion_Rate': 'mean',
                'ROI': 'mean',
                'Acquisition_Cost': 'mean'
            })
            
            for audience, row in audience_agg.iterrows():
                audience_performance.append({
                    'audience': audience,
                    'impressions': int(row['Impressions']),
                    'clicks': int(row['Clicks']),
                    'conversion_rate': round(row['Conversion_Rate'] * 100, 2),
                    'roi': round(row['ROI'], 2),
                    'acquisition_cost': round(row['Acquisition_Cost'], 2)
                })
        
        # Compile CAC data - limit to sample for performance
        # Take only the first 100 rows for performance
        cac_data = []
        sample_rows = df.head(100).iterrows()
        
        for _, row in sample_rows:
            cac_data.append({
                'campaign': row['Company'],
                'channel': row['Channel_Used'],
                'campaign_type': row['Campaign_Type'],
                'impressions': int(row['Impressions']),
                'clicks': int(row['Clicks']),
                'total_cost': round(float(row['Acquisition_Cost']), 2),
                'cac': round(float(row['Acquisition_Cost']), 2),
                'roi': round(float(row['ROI']), 2)
            })
        
        # Compile all results
        results = {
            'funnel': funnel,
            'conversion_rates': conversion_rates,
            'campaign_performance': campaign_performance,
            'channel_performance': channel_performance,
            'campaign_type_performance': campaign_type_performance,
            'audience_performance': audience_performance,
            'cac': cac_data
        }
        
        # Ensure all expected keys are present, even if empty
        expected_keys = [
            'funnel', 'conversion_rates', 'campaign_performance', 
            'channel_performance', 'cac'
        ]
        
        for key in expected_keys:
            if key not in results:
                if key in ['campaign_performance', 'channel_performance', 'cac']:
                    results[key] = []  # Empty list for list sections
                else:
                    results[key] = {}  # Empty dict for object sections
        
        # Save processed data to a file for future use
        data_dir = os.path.join(current_app.instance_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        data_path = os.path.join(data_dir, 'processed_data.json')
        with open(data_path, 'w') as f:
            json.dump(results, f)
            
        print(f"Saved processed data to {data_path} with sections: {list(results.keys())}")
        
        return results
        
    except Exception as e:
        print(f"Error processing marketing campaign data: {str(e)}")
        return {
            'error': str(e)
        }

def process_large_campaign_file(file_path):
    """
    Process large marketing campaign data file in chunks
    
    Args:
        file_path (str): Path to the large CSV file
    
    Returns:
        dict: Processed metrics and KPIs
    """
    try:
        # Initialize aggregation variables
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        total_conversion_rate_sum = 0
        total_roi_sum = 0
        total_acquisition_cost_sum = 0
        row_count = 0
        
        # Dictionaries to hold aggregated data
        company_data = {}
        channel_data = {}
        campaign_type_data = {}
        audience_data = {}
        
        # Sample rows for CAC data
        cac_samples = []
        sample_count = 0
        
        # Process in chunks of 10,000 rows
        for chunk in pd.read_csv(file_path, chunksize=10000):
            # Clean acquisition cost
            chunk['Acquisition_Cost'] = pd.to_numeric(
                chunk['Acquisition_Cost'].str.replace('$', '').str.replace(',', ''),
                errors='coerce'
            )
            
            # Update totals
            chunk_rows = len(chunk)
            row_count += chunk_rows
            total_impressions += chunk['Impressions'].sum()
            total_clicks += chunk['Clicks'].sum()
            total_conversion_rate_sum += chunk['Conversion_Rate'].sum()
            total_roi_sum += chunk['ROI'].sum()
            total_acquisition_cost_sum += chunk['Acquisition_Cost'].sum()
            
            # Update company aggregations
            for _, row in chunk.iterrows():
                company = row['Company']
                channel = row['Channel_Used']
                campaign_type = row['Campaign_Type']
                
                # Company data
                if company not in company_data:
                    company_data[company] = {
                        'impressions': 0, 'clicks': 0, 'conversion_sum': 0, 
                        'roi_sum': 0, 'acquisition_sum': 0, 'count': 0
                    }
                company_data[company]['impressions'] += row['Impressions']
                company_data[company]['clicks'] += row['Clicks']
                company_data[company]['conversion_sum'] += row['Conversion_Rate']
                company_data[company]['roi_sum'] += row['ROI']
                company_data[company]['acquisition_sum'] += row['Acquisition_Cost']
                company_data[company]['count'] += 1
                
                # Channel data
                if channel not in channel_data:
                    channel_data[channel] = {
                        'impressions': 0, 'clicks': 0, 'conversion_sum': 0, 
                        'roi_sum': 0, 'acquisition_sum': 0, 'count': 0
                    }
                channel_data[channel]['impressions'] += row['Impressions']
                channel_data[channel]['clicks'] += row['Clicks']
                channel_data[channel]['conversion_sum'] += row['Conversion_Rate']
                channel_data[channel]['roi_sum'] += row['ROI']
                channel_data[channel]['acquisition_sum'] += row['Acquisition_Cost']
                channel_data[channel]['count'] += 1
                
                # Campaign type data
                if campaign_type not in campaign_type_data:
                    campaign_type_data[campaign_type] = {
                        'impressions': 0, 'clicks': 0, 'conversion_sum': 0, 
                        'roi_sum': 0, 'acquisition_sum': 0, 'count': 0
                    }
                campaign_type_data[campaign_type]['impressions'] += row['Impressions']
                campaign_type_data[campaign_type]['clicks'] += row['Clicks']
                campaign_type_data[campaign_type]['conversion_sum'] += row['Conversion_Rate']
                campaign_type_data[campaign_type]['roi_sum'] += row['ROI']
                campaign_type_data[campaign_type]['acquisition_sum'] += row['Acquisition_Cost']
                campaign_type_data[campaign_type]['count'] += 1
                
                # Audience data if available
                if 'Target_Audience' in chunk.columns:
                    audience = row['Target_Audience']
                    if audience not in audience_data:
                        audience_data[audience] = {
                            'impressions': 0, 'clicks': 0, 'conversion_sum': 0, 
                            'roi_sum': 0, 'acquisition_sum': 0, 'count': 0
                        }
                    audience_data[audience]['impressions'] += row['Impressions']
                    audience_data[audience]['clicks'] += row['Clicks']
                    audience_data[audience]['conversion_sum'] += row['Conversion_Rate']
                    audience_data[audience]['roi_sum'] += row['ROI']
                    audience_data[audience]['acquisition_sum'] += row['Acquisition_Cost']
                    audience_data[audience]['count'] += 1
                
                # Collect sample rows for CAC data (limit to 100)
                if sample_count < 100:
                    cac_samples.append({
                        'campaign': row['Company'],
                        'channel': row['Channel_Used'],
                        'campaign_type': row['Campaign_Type'],
                        'impressions': int(row['Impressions']),
                        'clicks': int(row['Clicks']),
                        'total_cost': round(float(row['Acquisition_Cost']), 2),
                        'cac': round(float(row['Acquisition_Cost']), 2),
                        'roi': round(float(row['ROI']), 2)
                    })
                    sample_count += 1
        
        # Calculate averages
        avg_conversion_rate = (total_conversion_rate_sum / row_count) if row_count > 0 else 0
        avg_roi = (total_roi_sum / row_count) if row_count > 0 else 0
        avg_acquisition_cost = (total_acquisition_cost_sum / row_count) if row_count > 0 else 0
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        
        # Create funnel
        funnel = {
            'impressions': int(total_impressions),
            'clicks': int(total_clicks),
            'conversions': int(total_clicks * avg_conversion_rate)
        }
        
        # Conversion rates
        conversion_rates = {
            'click_through_rate': round(avg_ctr, 2),
            'conversion_rate': round(avg_conversion_rate * 100, 2),
            'roi': round(avg_roi, 2)
        }
        
        # Campaign performance - top companies by ROI
        campaign_performance = []
        for company, data in company_data.items():
            if data['count'] > 0:
                campaign_performance.append({
                    'campaign': company,
                    'impressions': int(data['impressions']),
                    'clicks': int(data['clicks']),
                    'conversion_rate': round((data['conversion_sum'] / data['count']) * 100, 2),
                    'roi': round(data['roi_sum'] / data['count'], 2),
                    'acquisition_cost': round(data['acquisition_sum'] / data['count'], 2)
                })
        
        # Sort by ROI and limit to top 10
        campaign_performance = sorted(
            campaign_performance, 
            key=lambda x: x['roi'], 
            reverse=True
        )[:10]
        
        # Channel performance
        channel_performance = []
        for channel, data in channel_data.items():
            if data['count'] > 0:
                channel_performance.append({
                    'channel': channel,
                    'impressions': int(data['impressions']),
                    'clicks': int(data['clicks']),
                    'conversion_rate': round((data['conversion_sum'] / data['count']) * 100, 2),
                    'roi': round(data['roi_sum'] / data['count'], 2),
                    'acquisition_cost': round(data['acquisition_sum'] / data['count'], 2)
                })
        
        # Sort by conversion rate
        channel_performance = sorted(
            channel_performance, 
            key=lambda x: x['conversion_rate'], 
            reverse=True
        )
        
        # Campaign type performance
        campaign_type_performance = []
        for campaign_type, data in campaign_type_data.items():
            if data['count'] > 0:
                campaign_type_performance.append({
                    'type': campaign_type,
                    'impressions': int(data['impressions']),
                    'clicks': int(data['clicks']),
                    'conversion_rate': round((data['conversion_sum'] / data['count']) * 100, 2),
                    'roi': round(data['roi_sum'] / data['count'], 2),
                    'acquisition_cost': round(data['acquisition_sum'] / data['count'], 2)
                })
        
        # Audience performance
        audience_performance = []
        for audience, data in audience_data.items():
            if data['count'] > 0:
                audience_performance.append({
                    'audience': audience,
                    'impressions': int(data['impressions']),
                    'clicks': int(data['clicks']),
                    'conversion_rate': round((data['conversion_sum'] / data['count']) * 100, 2),
                    'roi': round(data['roi_sum'] / data['count'], 2),
                    'acquisition_cost': round(data['acquisition_sum'] / data['count'], 2)
                })
        
        # Compile results
        results = {
            'funnel': funnel,
            'conversion_rates': conversion_rates,
            'campaign_performance': campaign_performance,
            'channel_performance': channel_performance,
            'campaign_type_performance': campaign_type_performance,
            'audience_performance': audience_performance,
            'cac': cac_samples
        }
        
        # Save processed data to a file for future use
        os.makedirs(os.path.join(current_app.instance_path, 'data'), exist_ok=True)
        with open(os.path.join(current_app.instance_path, 'data', 'processed_data.json'), 'w') as f:
            json.dump(results, f)
        
        return results
        
    except Exception as e:
        print(f"Error processing large marketing campaign data: {str(e)}")
        return {
            'error': str(e)
        }

def process_marketing_events_data(events_file_path):
    """
    Process marketing event data from CSV (original format)
    
    Args:
        events_file_path (str): Path to the events CSV file
    
    Returns:
        dict: Processed metrics and KPIs
    """
    try:
        # Read events data
        events_df = pd.read_csv(events_file_path)
        
        # Try to parse timestamps
        events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])
        
        # Basic data validation
        validate_csv(events_file_path, 'events')
        
        # Calculate funnel metrics
        funnel = {
            'page_view': int(events_df[events_df['event_type'] == 'page_view'].shape[0]),
            'signup': int(events_df[events_df['event_type'] == 'signup'].shape[0]),
            'purchase': int(events_df[events_df['event_type'] == 'purchase'].shape[0])
        }
        
        # Calculate conversion rates
        conversion_rates = {
            'signup_rate': round(funnel['signup'] / funnel['page_view'] * 100, 2) if funnel['page_view'] > 0 else 0,
            'purchase_rate': round(funnel['purchase'] / funnel['signup'] * 100, 2) if funnel['signup'] > 0 else 0,
            'overall_conversion': round(funnel['purchase'] / funnel['page_view'] * 100, 2) if funnel['page_view'] > 0 else 0
        }
        
        # Calculate campaign performance
        campaign_performance = []
        for campaign in events_df['campaign'].unique():
            campaign_data = events_df[events_df['campaign'] == campaign]
            views = int(campaign_data[campaign_data['event_type'] == 'page_view'].shape[0])
            signups = int(campaign_data[campaign_data['event_type'] == 'signup'].shape[0])
            purchases = int(campaign_data[campaign_data['event_type'] == 'purchase'].shape[0])
            
            campaign_performance.append({
                'campaign': campaign,
                'views': views,
                'signups': signups,
                'purchases': purchases,
                'signup_rate': round(signups / views * 100, 2) if views > 0 else 0,
                'purchase_rate': round(purchases / signups * 100, 2) if signups > 0 else 0
            })
        
        # Sort by conversion rate
        campaign_performance = sorted(
            campaign_performance, 
            key=lambda x: x['purchase_rate'] * x['signup_rate'], 
            reverse=True
        )
        
        # Calculate channel performance
        channel_performance = []
        for channel in events_df['channel'].unique():
            channel_data = events_df[events_df['channel'] == channel]
            views = int(channel_data[channel_data['event_type'] == 'page_view'].shape[0])
            signups = int(channel_data[channel_data['event_type'] == 'signup'].shape[0])
            purchases = int(channel_data[channel_data['event_type'] == 'purchase'].shape[0])
            
            channel_performance.append({
                'channel': channel,
                'views': views,
                'signups': signups,
                'purchases': purchases,
                'signup_rate': round(signups / views * 100, 2) if views > 0 else 0,
                'purchase_rate': round(purchases / signups * 100, 2) if signups > 0 else 0
            })
        
        # Try to calculate CAC if cost data is available
        cac_data = calculate_cac(events_df)
        
        # Compile all results
        results = {
            'funnel': funnel,
            'conversion_rates': conversion_rates,
            'campaign_performance': campaign_performance,
            'channel_performance': channel_performance
        }
        
        if cac_data:
            results['cac'] = cac_data
        
        # Save processed data to a file for future use
        os.makedirs(os.path.join(current_app.instance_path, 'data'), exist_ok=True)
        with open(os.path.join(current_app.instance_path, 'data', 'processed_data.json'), 'w') as f:
            json.dump(results, f)
        
        return results
        
    except Exception as e:
        return {
            'error': str(e)
        }


def load_campaign_costs(costs_file_path):
    """
    Load campaign cost data
    
    Args:
        costs_file_path (str): Path to the costs CSV file
    
    Returns:
        dict: Summary of loaded cost data
    """
    try:
        # Read cost data
        costs_df = pd.read_csv(costs_file_path)
        
        # Basic data validation
        validate_csv(costs_file_path, file_type='costs')
        
        # Save to a file for future use
        os.makedirs(os.path.join(current_app.instance_path, 'data'), exist_ok=True)
        costs_df.to_csv(os.path.join(current_app.instance_path, 'data', 'campaign_costs.csv'), index=False)
        
        # Return summary
        return {
            'campaigns': len(costs_df['campaign'].unique()),
            'channels': len(costs_df['channel'].unique()),
            'entries': len(costs_df)
        }
        
    except Exception as e:
        return {
            'error': str(e)
        }


def calculate_cac(events_df):
    """
    Calculate Customer Acquisition Cost based on campaign cost data
    
    Args:
        events_df (DataFrame): Events data
    
    Returns:
        list: CAC data by campaign and channel
    """
    # Check if costs data exists
    costs_path = os.path.join(current_app.instance_path, 'data', 'campaign_costs.csv')
    if not os.path.exists(costs_path):
        return None
    
    try:
        # Load costs data
        costs_df = pd.read_csv(costs_path)
        
        # Calculate acquisitions (purchases) per campaign and channel
        acquisitions = events_df[events_df['event_type'] == 'purchase'].groupby(
            ['campaign', 'channel']
        ).size().reset_index(name='acquisitions')
        
        # Calculate impressions for CPM calculation
        impressions = events_df[events_df['event_type'] == 'page_view'].groupby(
            ['campaign', 'channel']
        ).size().reset_index(name='impressions')
        
        # Calculate clicks for CPC calculation (signup events)
        clicks = events_df[events_df['event_type'] == 'signup'].groupby(
            ['campaign', 'channel']
        ).size().reset_index(name='clicks')
        
        # Merge data
        merged = acquisitions.merge(
            impressions, on=['campaign', 'channel'], how='outer'
        ).merge(
            clicks, on=['campaign', 'channel'], how='outer'
        ).merge(
            costs_df, on=['campaign', 'channel'], how='outer'
        )
        
        # Fill NaN values
        merged = merged.fillna({
            'acquisitions': 0,
            'impressions': 0,
            'clicks': 0,
            'cpc': 0,
            'cpm': 0
        })
        
        # Calculate costs
        merged['cpc_cost'] = merged['clicks'] * merged['cpc']
        merged['cpm_cost'] = merged['impressions'] * merged['cpm'] / 1000  # CPM is per 1000 impressions
        merged['total_cost'] = merged['cpc_cost'] + merged['cpm_cost']
        
        # Calculate CAC
        merged['cac'] = merged.apply(
            lambda row: row['total_cost'] / row['acquisitions'] if row['acquisitions'] > 0 else float('inf'),
            axis=1
        )
        
        # Prepare results
        cac_data = []
        for _, row in merged.iterrows():
            cac_data.append({
                'campaign': row['campaign'],
                'channel': row['channel'],
                'acquisitions': int(row['acquisitions']),
                'clicks': int(row['clicks']),
                'impressions': int(row['impressions']),
                'total_cost': round(float(row['total_cost']), 2),
                'cac': round(float(row['cac']), 2) if row['acquisitions'] > 0 else None
            })
        
        return cac_data
        
    except Exception as e:
        return {
            'error': str(e)
        }
