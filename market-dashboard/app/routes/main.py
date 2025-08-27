from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.data_service import process_marketing_data
import os
import json

bp = Blueprint('main', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
def index():
    """Main dashboard page"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Check if we have processed data
    data_path = os.path.join(current_app.instance_path, 'data', 'processed_data.json')
    flag_file = os.path.join(current_app.instance_path, 'data', 'initial_load_complete')
    
    # Force reprocessing if query param is provided
    force_reload = request.args.get('reload', '').lower() == 'true'
    
    if force_reload:
        # Remove the flag file to force reprocessing
        if os.path.exists(flag_file):
            os.remove(flag_file)
            print("Force reloading data: removed flag file")
    
    # Process data if needed (if flag file doesn't exist or processed data doesn't exist)
    if not os.path.exists(flag_file) or not os.path.exists(data_path):
        try:
            # First look for any uploaded files in the upload folder
            if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            upload_files = [f for f in os.listdir(current_app.config['UPLOAD_FOLDER']) 
                         if f.endswith('.csv') and os.path.isfile(os.path.join(current_app.config['UPLOAD_FOLDER'], f))]
            
            if upload_files:
                # Use the most recently modified file
                upload_files.sort(key=lambda x: os.path.getmtime(os.path.join(current_app.config['UPLOAD_FOLDER'], x)), 
                               reverse=True)
                latest_file = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_files[0])
                print(f"Processing most recent uploaded file: {latest_file}")
                
                # Make sure data directory exists
                os.makedirs(os.path.join(current_app.instance_path, 'data'), exist_ok=True)
                
                # Process the data
                from app.services.data_service import process_marketing_data
                process_marketing_data(latest_file, 'campaign')
            else:
                # Check if the default marketing_campaign_dataset.csv file exists
                csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                        'data', 'marketing_campaign_dataset.csv')
                if os.path.exists(csv_path):
                    print(f"Processing default dataset at {csv_path}")
                    
                    # Create directories if needed
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    os.makedirs(os.path.join(current_app.instance_path, 'data'), exist_ok=True)
                    
                    # Copy it to the upload folder and process it
                    import shutil
                    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'marketing_campaign_dataset.csv')
                    shutil.copy2(csv_path, upload_path)
                    
                    # Process the data
                    from app.services.data_service import process_marketing_data
                    result = process_marketing_data(upload_path, 'campaign')
                    
                    if result and 'error' in result:
                        print(f"Error processing data: {result['error']}")
                    else:
                        print("Data processed successfully")
            
            # Create the flag file to indicate initial load is complete
            with open(flag_file, 'w') as f:
                f.write('done')
                
            # Verify that processed_data.json exists
            if os.path.exists(data_path):
                print(f"Processed data file created at {data_path}")
                with open(data_path, 'r') as f:
                    data = json.load(f)
                print(f"Available sections: {list(data.keys())}")
            else:
                print(f"Warning: processed_data.json not created at {data_path}")
                
        except Exception as e:
            print(f"Error pre-processing marketing campaign data: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return render_template('dashboard.html')


@bp.route('/dashboard')
def dashboard():
    """Dashboard page - alternative route"""
    # Simply redirect to the index route which serves the dashboard
    return redirect(url_for('main.index'))


@bp.route('/analytics')
def analytics():
    """Advanced analytics page"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    return render_template('analytics.html')


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """File upload page"""
    # Only admins and editors can upload files
    if current_user.role not in ['admin', 'editor']:
        flash('Permission denied. You need to be an editor or admin to upload files.', 'error')
        return redirect(url_for('main.index'))

    return render_template('upload.html')
