import os
import pytest
import json
from unittest.mock import patch, MagicMock
from flask import url_for

class TestChartRendering:
    """Test cases for chart rendering and display"""
    
    def test_dashboard_loads_chart_styles(self, client, auth):
        """Test that chart-styles.css is loaded in the dashboard"""
        auth.login()
        response = client.get('/')
        assert response.status_code == 200
        assert b'chart-styles.css' in response.data
        assert b'chart-config.js' in response.data
        assert b'chart-reset.js' in response.data
        assert b'chart-manager.js' in response.data
    
    def test_chart_container_structure(self, client, auth):
        """Test that the chart containers have the correct structure for preventing growth"""
        auth.login()
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for chart container classes
        assert b'chart-container' in response.data
        assert b'chart-body' in response.data
        assert b'chart-canvas' in response.data
    
    def test_dashboard_api_endpoints_available(self, client, auth):
        """Test that all required API endpoints are available"""
        auth.login()
        
        # Test the main dashboard API endpoint
        response = client.get('/api/dashboard.json')
        assert response.status_code in [200, 404]  # 404 is acceptable if no data uploaded
        
        # Test section-specific endpoints
        sections = ['campaign_performance', 'channel_performance', 'cac']
        for section in sections:
            response = client.get(f'/api/dashboard/{section}.json')
            # Either 200 (success) or 404 (section not found/no data) are acceptable
            assert response.status_code in [200, 404]

    @patch('app.routes.api.os.path.exists')
    @patch('app.routes.api.open')
    def test_dashboard_data_processing(self, mock_open, mock_exists, client, auth):
        """Test that dashboard data is properly processed for chart rendering"""
        # Mock file existence
        mock_exists.return_value = True
        
        # Create mock data that simulates our processed data with funnel metrics
        mock_data = {
            'funnel': {
                'impressions': 10000,
                'clicks': 2500,
                'conversions': 500
            },
            'conversion_rates': {
                'click_through_rate': 25.0,
                'conversion_rate': 20.0,
                'roi': 300.0
            },
            'campaign_performance': [
                {'campaign_name': 'Campaign 1', 'roi': 250, 'conversion_rate': 15.0},
                {'campaign_name': 'Campaign 2', 'roi': 350, 'conversion_rate': 18.0}
            ],
            'channel_performance': [
                {'channel': 'Email', 'conversion_rate': 22.0, 'acquisition_cost': 12.50},
                {'channel': 'Social', 'conversion_rate': 18.0, 'acquisition_cost': 15.00}
            ]
        }
        
        # Mock the open function to return our test data
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
        
        auth.login()
        response = client.get('/api/dashboard.json')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert 'summary' in response_data
        assert 'funnel' in response_data['summary']
        assert 'conversion_rates' in response_data['summary']
        assert 'sections_available' in response_data
    
    @patch('app.routes.api.os.path.exists')
    @patch('app.routes.api.open')
    def test_campaign_performance_endpoint(self, mock_open, mock_exists, client, auth):
        """Test the campaign_performance endpoint specifically"""
        mock_exists.return_value = True
        
        # Mock campaign performance data
        mock_data = {
            'campaign_performance': [
                {'campaign_name': 'Campaign 1', 'roi': 250, 'conversion_rate': 15.0},
                {'campaign_name': 'Campaign 2', 'roi': 350, 'conversion_rate': 18.0}
            ]
        }
        
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
        
        auth.login()
        response = client.get('/api/dashboard/campaign_performance.json')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert 'data' in response_data
        assert len(response_data['data']) == 2
        assert 'meta' in response_data
    
    @patch('app.routes.api.os.path.exists')
    @patch('app.routes.api.open')
    def test_large_dataset_pagination(self, mock_open, mock_exists, client, auth):
        """Test that large datasets are properly paginated for charts"""
        mock_exists.return_value = True
        
        # Create a large dataset
        campaign_data = [
            {'campaign_name': f'Campaign {i}', 'roi': i * 10, 'conversion_rate': i * 1.5}
            for i in range(1, 31)
        ]
        
        mock_data = {
            'campaign_performance': campaign_data
        }
        
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)
        
        auth.login()
        
        # Test default pagination (page 1, per_page=10)
        response = client.get('/api/dashboard/campaign_performance.json')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert len(response_data['data']) == 10
        assert response_data['meta']['total'] == 30
        assert response_data['meta']['total_pages'] == 3
        
        # Test second page
        response = client.get('/api/dashboard/campaign_performance.json?page=2&per_page=10')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert len(response_data['data']) == 10
        assert response_data['data'][0]['campaign_name'] == 'Campaign 11'


class TestFileFormatCompatibility:
    """Test compatibility with different file formats including older Excel files"""
    
    def test_excel_file_validation(self, client, auth, tmpdir):
        """Test that Excel files can be validated"""
        auth.login()
        
        # We'll mock the file upload since we can't actually create Excel files here
        excel_content = b'PK\x03\x04' + b'\x00' * 100  # Fake Excel file header
        
        data = {
            'file': (BytesIO(excel_content), 'test_file.xlsx')
        }
        
        with patch('app.services.data_service.validate_csv') as mock_validate:
            mock_validate.return_value = {'valid': True, 'errors': []}
            response = client.post('/api/upload', data=data)
            
            # Check if the validate function was called
            assert mock_validate.called
    
    @patch('app.services.data_service.validate_csv')
    @patch('app.services.data_service.process_marketing_data')
    def test_excel_data_processing(self, mock_process, mock_validate, client, auth):
        """Test processing of data from Excel files"""
        auth.login()
        
        # Setup mocks to simulate successful validation and processing
        mock_validate.return_value = {'valid': True, 'errors': []}
        mock_process.return_value = {
            'records_processed': 150,
            'charts_generated': ['funnel', 'conversion']
        }
        
        # Create a fake Excel file content
        excel_content = b'PK\x03\x04' + b'\x00' * 100
        
        data = {
            'file': (BytesIO(excel_content), 'marketing_data.xlsx')
        }
        
        response = client.post('/api/upload', data=data)
        assert response.status_code == 200
        
        # Verify processing was called after validation
        assert mock_validate.called
        assert mock_process.called
        
        response_data = json.loads(response.data)
        assert 'message' in response_data
        assert 'summary' in response_data


# Pytest requires BytesIO to be imported for the file upload tests
from io import BytesIO
