import json
import pytest
from flask import url_for

def test_dashboard_json_endpoint_no_data(client, auth, app, monkeypatch):
    """Test dashboard.json endpoint when no data exists"""
    import os
    # Override the mock_processed_data fixture by ensuring the file doesn't exist
    data_path = os.path.join(app.instance_path, 'data', 'processed_data.json')
    if os.path.exists(data_path):
        os.remove(data_path)
    
    auth.login()
    response = client.get('/api/dashboard.json')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_dashboard_json_endpoint_with_data(client, auth, mock_processed_data):
    """Test dashboard.json endpoint returns correct data"""
    auth.login()
    response = client.get('/api/dashboard.json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'summary' in data
    assert 'sections_available' in data

def test_dashboard_section_endpoint(client, auth, mock_processed_data):
    """Test dashboard section endpoint with mock data"""
    auth.login()
    response = client.get('/api/dashboard/campaign_performance.json')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list) or ('data' in data and isinstance(data['data'], list))

def test_dashboard_invalid_section(client, auth, mock_processed_data):
    """Test dashboard with invalid section"""
    auth.login()
    response = client.get('/api/dashboard/invalid_section.json')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_dashboard_section_sorting_and_pagination(client, auth, mock_processed_data):
    """Test sorting and pagination on sections that support it"""
    auth.login()
    response = client.get('/api/dashboard/cac.json?page=1&per_page=5&sort_by=roi&sort_dir=desc')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert 'meta' in data
    assert data['meta']['page'] == 1
    assert data['meta']['per_page'] == 5
