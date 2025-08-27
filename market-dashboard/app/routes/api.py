import json
import os
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from app.services.data_service import validate_csv, process_marketing_data, load_campaign_costs
from app.services.data_enhancement import get_enhanced_data

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/healthz', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0'
    })


@bp.route('/dashboard.json', methods=['GET'])
@login_required
def dashboard_data():
    """Return dashboard data in JSON format"""
    try:
        # Get query parameters for pagination/filtering
        section = request.args.get('section', None)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limit per_page to prevent excessive data retrieval
        per_page = min(per_page, 50)
        
        # In a real app, we would get this from a database
        # For now, we'll read from processed files if they exist
        data_path = os.path.join(current_app.instance_path, 'data', 'processed_data.json')
        if os.path.exists(data_path):
            # Use caching based on modification time
            # Check if we already have the data cached in memory
            cache_key = f"dashboard_data_{os.path.getmtime(data_path)}"
            cached_data = getattr(current_app, cache_key, None)
            
            if cached_data is None:
                # Not cached, load from file
                with open(data_path, 'r') as f:
                    cached_data = json.load(f)
                # Store in app context for future requests
                setattr(current_app, cache_key, cached_data)
            
            # If a specific section is requested, return only that section
            if section and section in cached_data:
                section_data = cached_data[section]
                
                # Apply pagination if the section is a list
                if isinstance(section_data, list):
                    total = len(section_data)
                    start = (page - 1) * per_page
                    end = start + per_page
                    
                    # Return paginated data with metadata
                    return jsonify({
                        'data': section_data[start:end],
                        'meta': {
                            'page': page,
                            'per_page': per_page,
                            'total': total,
                            'total_pages': (total + per_page - 1) // per_page
                        }
                    })
                else:
                    # Return non-list data directly
                    return jsonify(section_data)
            else:
                # Return all sections (or error if section not found)
                if section:
                    return jsonify({
                        'error': f'Section {section} not found'
                    }), 404
                else:
                    # For the full dataset, we could add a summary instead of sending everything
                    # to improve performance for the initial dashboard load
                    return jsonify({
                        'summary': {
                            'funnel': cached_data.get('funnel', {}),
                            'conversion_rates': cached_data.get('conversion_rates', {})
                        },
                        'sections_available': list(cached_data.keys())
                    })
        else:
            return jsonify({
                'error': 'No data available. Please upload marketing event data.'
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving dashboard data: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500


@bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """API endpoint to upload CSV files"""
    # Check if user has permission to upload
    if current_user.role not in ['admin', 'editor']:
        return jsonify({
            'error': 'Permission denied. You need to be an editor or admin to upload files.'
        }), 403

    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file part in the request'
        }), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({
            'error': 'No selected file'
        }), 400
    
    file_type = request.form.get('file_type', 'campaign')
    
    if file and allowed_file(file.filename):
        # Ensure upload directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        print(f"File saved to {file_path}")
        
        # Validate the CSV
        validation_result = validate_csv(file_path, file_type)
        if validation_result['valid'] or file_type == 'campaign':  # For campaign type, we'll be more lenient
            try:
                # Process the file based on type
                if file_type == 'campaign':
                    # Process campaign data
                    print(f"Processing campaign data from {file_path}")
                    result = process_marketing_data(file_path, 'campaign')
                    
                    # Delete any flag file to force reprocessing
                    flag_file = os.path.join(current_app.instance_path, 'data', 'initial_load_complete')
                    if os.path.exists(flag_file):
                        os.remove(flag_file)
                        
                    # Verify that processed_data.json was created
                    data_file = os.path.join(current_app.instance_path, 'data', 'processed_data.json')
                    if os.path.exists(data_file):
                        with open(data_file, 'r') as f:
                            processed_data = json.load(f)
                        print(f"Processed data sections: {list(processed_data.keys())}")
                    else:
                        print(f"Warning: processed_data.json was not created at {data_file}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Marketing campaign data uploaded and processed successfully',
                        'summary': result,
                        'redirect': '/dashboard'
                    })
                elif file_type == 'events':
                    # Process events data
                    print(f"Processing events data from {file_path}")
                    result = process_marketing_data(file_path, 'events')
                    return jsonify({
                        'success': True,
                        'message': 'Marketing event data uploaded and processed successfully',
                        'summary': result,
                        'redirect': '/dashboard'
                    })
                elif file_type == 'costs':
                    # Process campaign costs data
                    print(f"Processing costs data from {file_path}")
                    result = load_campaign_costs(file_path)
                    return jsonify({
                        'success': True,
                        'message': 'Campaign cost data uploaded successfully',
                        'summary': result,
                        'redirect': '/dashboard'
                    })
            except Exception as e:
                print(f"Error processing uploaded file: {str(e)}")
                return jsonify({
                    'error': f'Error processing file: {str(e)}'
                }), 500
        else:
            # Return validation errors
            return jsonify({
                'error': 'Invalid file format',
                'details': validation_result['errors']
            }), 400
    
    return jsonify({
        'error': 'File type not allowed'
    }), 400


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/data/<section>', methods=['GET'])
@login_required
def get_section_data(section):
    """Get specific data section with pagination support"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', None)
        sort_dir = request.args.get('sort_dir', 'desc')
        
        # Limit per_page to prevent excessive data retrieval
        per_page = min(per_page, 100)
        
        # Get data from processed file
        data_path = os.path.join(current_app.instance_path, 'data', 'processed_data.json')
        if os.path.exists(data_path):
            # Use caching based on modification time
            cache_key = f"dashboard_data_{os.path.getmtime(data_path)}"
            cached_data = getattr(current_app, cache_key, None)
            
            if cached_data is None:
                # Not cached, load from file
                with open(data_path, 'r') as f:
                    cached_data = json.load(f)
                # Store in app context for future requests
                setattr(current_app, cache_key, cached_data)
            
            # Print available sections for debugging
            available_sections = list(cached_data.keys())
            print(f"Available sections in processed data: {available_sections}")
            
            # Check if the requested section exists
            if section not in cached_data:
                # Check for common naming mismatches
                section_mapping = {
                    'campaign': 'campaign_performance',
                    'campaigns': 'campaign_performance',
                    'channel': 'channel_performance',
                    'channels': 'channel_performance',
                    'campaign_type': 'campaign_type_performance',
                    'audience': 'audience_performance'
                }
                
                if section in section_mapping and section_mapping[section] in cached_data:
                    # Use the mapped section name
                    section = section_mapping[section]
                else:
                    return jsonify({
                        'error': f'Section {section} not found',
                        'available_sections': available_sections
                    }), 404
            
            section_data = cached_data[section]
            print(f"Retrieved data for section {section}")
            
            # Only apply pagination and sorting for list data
            if isinstance(section_data, list):
                # Apply sorting if requested and the field exists
                if sort_by and sort_by in section_data[0] if section_data else False:
                    section_data = sorted(
                        section_data,
                        key=lambda x: x.get(sort_by, 0),
                        reverse=(sort_dir.lower() == 'desc')
                    )
                
                # Apply pagination
                total = len(section_data)
                start = (page - 1) * per_page
                end = start + per_page
                
                return jsonify({
                    'data': section_data[start:end],
                    'meta': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'total_pages': (total + per_page - 1) // per_page,
                        'sort_by': sort_by,
                        'sort_dir': sort_dir
                    }
                })
            else:
                # Return non-list data directly
                return jsonify(section_data)
        else:
            return jsonify({
                'error': 'No data available. Please upload marketing event data.'
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving section data: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500


# Add section-specific endpoints for dashboard data
@bp.route('/dashboard/<section>.json', methods=['GET'])
@login_required
def dashboard_section(section):
    """Return specific section of dashboard data"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', None)
        sort_dir = request.args.get('sort_dir', 'desc')
        
        # Get data from processed file
        data_path = os.path.join(current_app.instance_path, 'data', 'processed_data.json')
        if os.path.exists(data_path):
            # Use caching based on modification time
            cache_key = f"dashboard_data_{os.path.getmtime(data_path)}"
            cached_data = getattr(current_app, cache_key, None)
            
            if cached_data is None:
                # Not cached, load from file
                with open(data_path, 'r') as f:
                    cached_data = json.load(f)
                # Store in app context for future requests
                setattr(current_app, cache_key, cached_data)
            
            # Handle section mappings for consistency
            section_mapping = {
                'campaign_performance': ['campaign_performance', 'campaigns', 'campaign'],
                'channel_performance': ['channel_performance', 'channels', 'channel'],
                'cac': ['cac', 'acquisition_cost', 'customer_acquisition'],
                'enhanced_cac': ['enhanced_cac', 'enhanced_acquisition_cost']
            }
            
            # Find the correct section key
            actual_section = section
            for key, aliases in section_mapping.items():
                if section in aliases and key in cached_data:
                    actual_section = key
                    break
            
            # Special handling for CAC data - use enhanced version if available
            if section in ['cac', 'acquisition_cost', 'customer_acquisition']:
                enhanced_data = get_enhanced_data()
                if enhanced_data and 'enhanced_cac' in enhanced_data:
                    section_data = enhanced_data['enhanced_cac']
                elif actual_section in cached_data:
                    section_data = cached_data[actual_section]
                else:
                    return jsonify({
                        'error': f'Section {section} not found',
                        'available_sections': list(cached_data.keys())
                    }), 404
            elif actual_section not in cached_data:
                return jsonify({
                    'error': f'Section {section} not found',
                    'available_sections': list(cached_data.keys())
                }), 404
            else:
                section_data = cached_data[actual_section]
            
            # Only apply pagination and sorting for list data
            if isinstance(section_data, list):
                # Apply sorting if requested
                if sort_by and len(section_data) > 0 and sort_by in section_data[0]:
                    section_data = sorted(
                        section_data,
                        key=lambda x: x.get(sort_by, 0),
                        reverse=(sort_dir.lower() == 'desc')
                    )
                
                # Apply pagination
                total = len(section_data)
                start = (page - 1) * per_page
                end = start + per_page
                
                return jsonify({
                    'data': section_data[start:end],
                    'meta': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'total_pages': (total + per_page - 1) // per_page,
                        'sort_by': sort_by,
                        'sort_dir': sort_dir
                    }
                })
            else:
                # Return non-list data directly
                return jsonify(section_data)
        else:
            return jsonify({
                'error': 'No data available. Please upload marketing event data.'
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving dashboard section data: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500
