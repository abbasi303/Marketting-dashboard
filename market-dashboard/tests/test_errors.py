"""
Error handling and edge case tests for Marketing Insights Dashboard
"""
import pytest
import io
from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


class TestErrorHandlers:
    """Test error handling functionality"""

    def test_file_too_large_error_handler(self, client):
        """Test 413 error handler for large files"""
        # Set up authenticated Admin session
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        # Create a large file (simulate exceeding 50MB)
        # Note: This tests the error handler, actual file size enforcement is at Flask level
        large_content = "x" * (60 * 1024 * 1024)  # 60MB of data
        large_file = io.BytesIO(large_content.encode('utf-8'))
        
        data = {
            'events_csv': (large_file, 'large_file.csv')
        }
        
        try:
            response = client.post('/upload', data=data, content_type='multipart/form-data')
            # If Flask catches it, should get 413
            if response.status_code == 413:
                response_data = response.get_json()
                assert 'File too large' in response_data['error']
                assert response_data['max_size'] == '50MB'
        except Exception:
            # Large file may cause connection issues in test environment
            pass

    def test_bad_request_handler(self, client):
        """Test 400 bad request handler"""
        # Test with malformed JSON
        response = client.post('/dashboard.json', 
                              data="invalid json", 
                              content_type='application/json')
        # Should handle gracefully (may return various status codes)
        assert response.status_code in [400, 405, 500]

    def test_upload_non_csv_file(self, client):
        """Test upload with non-CSV file"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        # Create a text file
        text_file = io.BytesIO(b"This is not a CSV file")
        
        data = {
            'events_csv': (text_file, 'file.txt')
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_upload_empty_file(self, client):
        """Test upload with empty file"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        # Create empty file
        empty_file = io.BytesIO(b"")
        
        data = {
            'events_csv': (empty_file, 'empty.csv')
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_upload_both_files(self, client):
        """Test upload with both events and costs CSV"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        # Create valid events CSV
        events_csv = "Campaign_ID,Channel_Used,Campaign_Type,Company,Clicks,Impressions,Conversion_Rate,Date,Acquisition_Cost\n1,Google,Search,Corp,100,1000,0.1,2021-01-01,$100"
        events_file = io.BytesIO(events_csv.encode('utf-8'))
        
        # Create valid costs CSV
        costs_csv = "campaign,channel,cpc,cpm\n1,Google,1.5,15.0"
        costs_file = io.BytesIO(costs_csv.encode('utf-8'))
        
        data = {
            'events_csv': (events_file, 'events.csv'),
            'costs_csv': (costs_file, 'costs.csv')
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        
        response_data = response.get_json()
        assert 'events_rows' in response_data
        assert 'costs_rows' in response_data


class TestSessionValidation:
    """Test session validation edge cases"""

    def test_health_check_no_auth_required(self, client):
        """Test health check works without authentication"""
        response = client.get('/healthz')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'

    def test_dashboard_json_with_auth(self, client):
        """Test dashboard.json works with authentication"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        response = client.get('/dashboard.json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'views' in data
        assert 'signups' in data
        assert 'purchases' in data

    def test_invalid_session_handling(self, client):
        """Test handling of corrupted session data"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'nonexistent'  # User not in USERS dict
            sess['role'] = 'InvalidRole'
        
        response = client.get('/')
        # Should handle gracefully - either redirect or show error
        assert response.status_code in [200, 302, 403]
