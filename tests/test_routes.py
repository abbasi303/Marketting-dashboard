import os
import tempfile
import pytest
from flask import url_for
from io import BytesIO


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/api/healthz')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'ok'


def test_index_redirect_if_not_logged_in(client):
    """Test that index redirects to login if not logged in"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_index_logged_in(client, auth):
    """Test that index works if logged in"""
    auth.login()
    response = client.get('/')
    assert response.status_code == 200
    assert b'Marketing Performance Dashboard' in response.data


def test_analytics_page(client, auth):
    """Test the analytics page loads correctly"""
    auth.login()
    response = client.get('/analytics')
    assert response.status_code == 200
    assert b'Marketing Performance Analytics' in response.data


def test_login(client):
    """Test login functionality"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data
    
    # Test valid login
    response = client.post(
        '/auth/login',
        data={'username': 'admin', 'password': 'adminpass'}
    )
    assert response.status_code == 302
    assert '/' in response.location
    
    # Test invalid username
    response = client.post(
        '/auth/login',
        data={'username': 'notauser', 'password': 'password'}
    )
    assert response.status_code == 200
    assert b'Invalid username' in response.data
    
    # Test invalid password
    response = client.post(
        '/auth/login',
        data={'username': 'admin', 'password': 'wrongpassword'}
    )
    assert response.status_code == 200
    assert b'Invalid password' in response.data


def test_logout(client, auth):
    """Test logout functionality"""
    auth.login()
    
    with client:
        auth.logout()
        response = client.get('/')
        assert response.status_code == 302
        assert '/auth/login' in response.location


def test_upload_access_control(client, auth):
    """Test that only admins and editors can access upload page"""
    # Test with viewer (should be denied)
    auth.login(username='viewer', password='viewerpass')
    response = client.get('/upload')
    assert response.status_code == 302  # Should redirect back to index
    
    # Test with editor (should be allowed)
    auth.login(username='editor', password='editorpass')
    response = client.get('/upload')
    assert response.status_code == 200
    assert b'Upload Marketing Data Files' in response.data
    
    # Test with admin (should be allowed)
    auth.login(username='admin', password='adminpass')
    response = client.get('/upload')
    assert response.status_code == 200
    assert b'Upload Marketing Data Files' in response.data


def test_api_upload_events(client, auth):
    """Test API upload endpoint for events file"""
    auth.login(username='admin', password='adminpass')
    
    # Get the path to the sample events file
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    file_path = os.path.join(data_dir, 'sample_events.csv')
    
    # Read the file content
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Create file data for upload
    data = {
        'file': (BytesIO(file_content), 'sample_events.csv'),
        'file_type': 'events'
    }
    
    response = client.post(
        '/api/upload',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True
    assert 'summary' in json_data
    assert 'funnel' in json_data['summary']


def test_api_upload_costs(client, auth):
    """Test API upload endpoint for costs file"""
    auth.login(username='admin', password='adminpass')
    
    # Get the path to the sample costs file
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    file_path = os.path.join(data_dir, 'sample_costs.csv')
    
    # Read the file content
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Create file data for upload
    data = {
        'file': (BytesIO(file_content), 'sample_costs.csv'),
        'file_type': 'costs'
    }
    
    response = client.post(
        '/api/upload',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True
    assert 'summary' in json_data
    assert 'campaigns' in json_data['summary']


def test_api_upload_invalid_file(client, auth):
    """Test API upload endpoint with invalid file"""
    auth.login(username='admin', password='adminpass')
    
    # Create an invalid file
    with tempfile.NamedTemporaryFile(suffix='.csv') as f:
        f.write(b'invalid,file\n1,2,3')
        f.seek(0)
        
        data = {
            'file': (f, 'invalid.csv'),
            'file_type': 'events'
        }
        
        response = client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'details' in json_data


def test_api_upload_permission_denied(client, auth):
    """Test that viewers cannot upload files"""
    auth.login(username='viewer', password='viewerpass')
    
    # Get the path to the sample events file
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    file_path = os.path.join(data_dir, 'sample_events.csv')
    
    # Read the file content
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Create file data for upload
    data = {
        'file': (BytesIO(file_content), 'sample_events.csv'),
        'file_type': 'events'
    }
    
    response = client.post(
        '/api/upload',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 403
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'permission' in json_data['error'].lower()
