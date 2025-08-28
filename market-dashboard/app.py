import os
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_PATH'] = 50 * 1024 * 1024

# Global storage for uploaded data
uploaded_data = {
    'events_df': None,
    'costs_df': None,
    'last_upload': None
}

# RBAC roles and users (in production, use proper authentication)
ROLES = ['Admin', 'Editor', 'Viewer']
USERS = {
    'admin': {'password': 'admin123', 'role': 'Admin'},
    'editor': {'password': 'editor123', 'role': 'Editor'},
    'viewer': {'password': 'viewer123', 'role': 'Viewer'},
    'demo': {'password': 'demo', 'role': 'Admin'}  # Easy demo login
}

def get_current_user():
    """Get current logged-in user"""
    return session.get('username')

def get_current_role():
    """Get current user role from session"""
    if not session.get('logged_in'):
        return None
    username = session.get('username')
    if username in USERS:
        return USERS[username]['role']
    return session.get('role', 'Viewer')

def requires_login():
    """Check if user is logged in"""
    return session.get('logged_in', False)

def requires_upload_permission():
    """Check if current role can upload data"""
    if not requires_login():
        return False
    role = get_current_role()
    return role in ['Admin', 'Editor']

def parse_currency(value):
    """Parse currency string to float"""
    if pd.isna(value) or value == '':
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    
    # Remove currency symbols and commas
    cleaned = re.sub(r'[$,€£¥]', '', str(value))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def validate_events_csv(df):
    """Validate events CSV has required columns"""
    required_columns = ['Campaign_ID', 'Channel_Used', 'Clicks', 'Impressions', 'Conversion_Rate', 'Date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {missing_columns}"
    
    return True, "Valid"

def validate_costs_csv(df):
    """Validate costs CSV has required columns"""
    required_columns = ['campaign', 'channel', 'cpc', 'cpm']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {missing_columns}"
    
    return True, "Valid"

def clean_and_validate_data(df):
    """Clean and validate the uploaded data"""
    # Parse date column
    try:
        df['Date'] = pd.to_datetime(df['Date'])
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")
    
    # Ensure numeric columns are numeric
    numeric_columns = ['Clicks', 'Impressions', 'Conversion_Rate']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Parse Acquisition_Cost if present
    if 'Acquisition_Cost' in df.columns:
        df['Acquisition_Cost_Parsed'] = df['Acquisition_Cost'].apply(parse_currency)
    
    # Remove rows with critical missing data
    df = df.dropna(subset=['Campaign_ID', 'Channel_Used', 'Clicks', 'Impressions', 'Conversion_Rate'])
    
    return df

def calculate_kpis(events_df, costs_df=None):
    """Calculate KPIs from the uploaded data"""
    if events_df is None or events_df.empty:
        return {
            'views': 0,
            'signups': 0,
            'purchases': 0,
            'signup_view_rate': 0.0,
            'purchase_signup_rate': 0.0,
            'estimated_cac': 0.0,
            'top_campaigns': []
        }
    
    # Basic KPIs
    views = int(events_df['Impressions'].sum())
    signups = int(events_df['Clicks'].sum())
    purchases = int((events_df['Clicks'] * events_df['Conversion_Rate']).round().sum())
    
    # Rates
    signup_view_rate = signups / views if views > 0 else 0.0
    purchase_signup_rate = purchases / signups if signups > 0 else 0.0
    
    # Calculate CAC (fixed)
    estimated_cac = 0.0
    if costs_df is not None and not costs_df.empty:
        # Use costs CSV to calculate CAC
        merged_df = events_df.merge(
            costs_df,
            left_on=['Campaign_ID', 'Channel_Used'],
            right_on=['campaign', 'channel'],
            how='left'
        )
        merged_df['cpc'] = pd.to_numeric(merged_df['cpc'], errors='coerce').fillna(0)
        merged_df['cpm'] = pd.to_numeric(merged_df['cpm'], errors='coerce').fillna(0)
        merged_df['campaign_purchases'] = (merged_df['Clicks'] * merged_df['Conversion_Rate']).round()
        merged_df['total_cost'] = (merged_df['Impressions'] / 1000 * merged_df['cpm'] + 
                                  merged_df['Clicks'] * merged_df['cpc'])
        
        total_cost = merged_df['total_cost'].sum()
        total_purchases = merged_df['campaign_purchases'].sum()
        estimated_cac = total_cost / total_purchases if total_purchases > 0 else 0.0
    elif 'Acquisition_Cost_Parsed' in events_df.columns and events_df['Acquisition_Cost_Parsed'].sum() > 0:
        # Use acquisition cost from events CSV (weighted average)
        events_df['campaign_purchases'] = (events_df['Clicks'] * events_df['Conversion_Rate']).round()
        # Calculate weighted average CAC
        total_weighted_cost = (events_df['Acquisition_Cost_Parsed'] * events_df['campaign_purchases']).sum()
        total_purchases = events_df['campaign_purchases'].sum()
        estimated_cac = total_weighted_cost / total_purchases if total_purchases > 0 else 0.0
    elif 'Acquisition_Cost' in events_df.columns:
        # Try to parse acquisition cost on the fly
        events_df['temp_cost'] = events_df['Acquisition_Cost'].apply(parse_currency)
        events_df['campaign_purchases'] = (events_df['Clicks'] * events_df['Conversion_Rate']).round()
        total_weighted_cost = (events_df['temp_cost'] * events_df['campaign_purchases']).sum()
        total_purchases = events_df['campaign_purchases'].sum()
        estimated_cac = total_weighted_cost / total_purchases if total_purchases > 0 else 0.0
    
    # Top campaigns by Purchase/Signup rate (fixed calculation)
    # Calculate actual conversion rate per campaign group
    campaign_stats = events_df.groupby(['Campaign_ID', 'Channel_Used']).agg({
        'Clicks': 'sum',
        'Impressions': 'sum',
        'Conversion_Rate': 'mean',  # Keep for reference, but recalculate below
        'Company': 'first',  # Get company name
        'Campaign_Type': 'first'  # Get campaign type
    }).reset_index()
    
    # Calculate purchases and actual conversion rate
    campaign_stats['purchases'] = (campaign_stats['Clicks'] * campaign_stats['Conversion_Rate']).round()
    campaign_stats['actual_conversion_rate'] = campaign_stats['purchases'] / campaign_stats['Clicks']
    campaign_stats['actual_conversion_rate'] = campaign_stats['actual_conversion_rate'].fillna(0)
    campaign_stats['ctr'] = (campaign_stats['Clicks'] / campaign_stats['Impressions'] * 100).round(2)
    
    # Filter out campaigns with zero clicks and sort by actual performance metrics
    campaign_stats_filtered = campaign_stats[campaign_stats['Clicks'] > 0].copy()
    
    # Create performance score combining conversion rate and volume
    campaign_stats_filtered['performance_score'] = (
        campaign_stats_filtered['actual_conversion_rate'] * 0.7 + 
        (campaign_stats_filtered['purchases'] / campaign_stats_filtered['purchases'].max()) * 0.3
    )
    
    top_campaigns = campaign_stats_filtered.nlargest(10, 'performance_score')[
        ['Campaign_ID', 'Channel_Used', 'actual_conversion_rate', 'Clicks', 'Impressions', 'purchases', 'Company', 'ctr']
    ].to_dict('records')
    
    # Rename for frontend compatibility
    for campaign in top_campaigns:
        campaign['purchase_signup_rate'] = campaign.pop('actual_conversion_rate')
    
    # Channel performance (fixed aggregation)
    channel_performance = events_df.groupby('Channel_Used').agg({
        'Clicks': 'sum',
        'Impressions': 'sum',
        'Conversion_Rate': 'mean',  # Average of individual rates
        'Acquisition_Cost': lambda x: pd.to_numeric(x.astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce').mean()
    }).reset_index()
    
    # Calculate channel metrics properly
    channel_performance['purchases'] = (channel_performance['Clicks'] * channel_performance['Conversion_Rate']).round().astype(int)
    channel_performance['ctr'] = (channel_performance['Clicks'] / channel_performance['Impressions'] * 100).round(2)
    channel_performance['actual_conversion_rate'] = (channel_performance['purchases'] / channel_performance['Clicks'] * 100).round(2)
    channel_performance = channel_performance.sort_values('purchases', ascending=False)
    
    # Time series data (improved)
    events_df['Date'] = pd.to_datetime(events_df['Date'], errors='coerce')
    events_df['month'] = events_df['Date'].dt.to_period('M').astype(str)
    
    monthly_performance = events_df.groupby('month').agg({
        'Clicks': 'sum',
        'Impressions': 'sum',
        'Conversion_Rate': 'mean'
    }).reset_index()
    monthly_performance['purchases'] = (monthly_performance['Clicks'] * monthly_performance['Conversion_Rate']).round().astype(int)
    monthly_performance['ctr'] = (monthly_performance['Clicks'] / monthly_performance['Impressions'] * 100).round(2)
    
    # Sort by month
    monthly_performance = monthly_performance.sort_values('month')
    
    # Company performance
    if 'Company' in events_df.columns:
        company_performance = events_df.groupby('Company').agg({
            'Clicks': 'sum',
            'Impressions': 'sum',
            'Conversion_Rate': 'mean'
        }).reset_index()
        company_performance['purchases'] = (company_performance['Clicks'] * company_performance['Conversion_Rate']).round()
        company_performance['ctr'] = (company_performance['Clicks'] / company_performance['Impressions'] * 100).round(2)
    else:
        company_performance = pd.DataFrame()
    
    return {
        'views': views,
        'signups': signups,
        'purchases': purchases,
        'signup_view_rate': round(signup_view_rate * 100, 2),
        'purchase_signup_rate': round(purchase_signup_rate * 100, 2),
        'estimated_cac': round(estimated_cac, 2),
        'top_campaigns': top_campaigns,
        'channel_performance': channel_performance.to_dict('records'),
        'monthly_performance': monthly_performance.to_dict('records'),
        'company_performance': company_performance.to_dict('records') if not company_performance.empty else [],
        # Additional insights
        'data_quality': {
            'total_campaigns': len(events_df['Campaign_ID'].unique()),
            'total_channels': len(events_df['Channel_Used'].unique()),
            'date_range': {
                'start': events_df['Date'].min() if 'Date' in events_df.columns else None,
                'end': events_df['Date'].max() if 'Date' in events_df.columns else None
            },
            'avg_ctr': round(signups / views * 100, 2) if views > 0 else 0,
            'top_performing_channel': channel_performance.iloc[0]['Channel_Used'] if not channel_performance.empty else None,
            'best_campaign_rate': round(campaign_stats_filtered['actual_conversion_rate'].max() * 100, 2) if not campaign_stats_filtered.empty else 0
        }
    }

@app.route('/')
def dashboard():
    """Main dashboard page"""
    if not requires_login():
        return redirect(url_for('login'))
    return render_template('dashboard_new.html', role=get_current_role(), username=get_current_user())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        
        if username in USERS and USERS[username]['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = USERS[username]['role']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/set-role', methods=['GET', 'POST'])
def set_role():
    """Set user role for session (Admin only)"""
    if not requires_login():
        return redirect(url_for('login'))
    
    current_role = get_current_role()
    if current_role != 'Admin':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        role = request.form.get('role')
        if role in ROLES:
            session['role'] = role
        return redirect(url_for('dashboard'))
    
    return render_template('set_role_new.html', roles=ROLES, current_role=get_current_role())

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large. Maximum file size is 50MB.',
        'max_size': '50MB'
    }), 413

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """Handle RequestEntityTooLarge exception"""
    return jsonify({
        'error': 'File too large. Maximum file size is 50MB.',
        'max_size': '50MB'
    }), 413

@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        'error': 'Bad request',
        'message': str(error)
    }), 400

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        if not requires_upload_permission():
            return jsonify({'error': 'Insufficient permissions. Admin or Editor role required.'}), 403
        
        if 'events_csv' not in request.files:
            return jsonify({'error': 'events_csv file is required'}), 400
        
        events_file = request.files['events_csv']
        costs_file = request.files.get('costs_csv')
        
        if events_file.filename == '':
            return jsonify({'error': 'No events file selected'}), 400
        
        # Check file size explicitly
        if events_file.content_length and events_file.content_length > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({
                'error': f'Events file too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB'
            }), 413
        
        if costs_file and costs_file.content_length and costs_file.content_length > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({
                'error': f'Costs file too large. Maximum size is {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB'
            }), 413
        
        # Read and validate events CSV
        try:
            events_df = pd.read_csv(events_file)
        except pd.errors.EmptyDataError:
            return jsonify({'error': 'Events CSV file is empty'}), 400
        except pd.errors.ParserError as e:
            return jsonify({'error': f'Error parsing events CSV: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': f'Error reading events CSV: {str(e)}'}), 400
        
        is_valid, error_msg = validate_events_csv(events_df)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        events_df = clean_and_validate_data(events_df)
        if events_df.empty:
            return jsonify({'error': 'No valid data found in events CSV after validation'}), 400
        
        uploaded_data['events_df'] = events_df
        
        # Read costs CSV if provided
        costs_df = None
        if costs_file and costs_file.filename != '':
            try:
                costs_df = pd.read_csv(costs_file)
                is_valid, error_msg = validate_costs_csv(costs_df)
                if not is_valid:
                    return jsonify({'error': f"Costs CSV validation failed: {error_msg}"}), 400
                uploaded_data['costs_df'] = costs_df
            except pd.errors.EmptyDataError:
                return jsonify({'error': 'Costs CSV file is empty'}), 400
            except pd.errors.ParserError as e:
                return jsonify({'error': f'Error parsing costs CSV: {str(e)}'}), 400
            except Exception as e:
                return jsonify({'error': f'Error reading costs CSV: {str(e)}'}), 400
        
        uploaded_data['last_upload'] = datetime.now()
        
        return jsonify({
            'message': 'Files uploaded successfully',
            'events_rows': len(events_df),
            'costs_rows': len(costs_df) if costs_df is not None else 0
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Unexpected error during file upload',
            'message': str(e)
        }), 500
        
    except Exception as e:
        return jsonify({'error': f'Error processing files: {str(e)}'}), 400

@app.route('/dashboard.json')
def dashboard_json():
    """Get dashboard KPIs as JSON"""
    try:
        kpis = calculate_kpis(uploaded_data['events_df'], uploaded_data['costs_df'])
        kpis['last_update'] = uploaded_data['last_upload'].isoformat() if uploaded_data['last_upload'] else None
        return jsonify(kpis)
    except Exception as e:
        return jsonify({'error': f'Error calculating KPIs: {str(e)}'}), 500

@app.route('/healthz')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': uploaded_data['events_df'] is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
