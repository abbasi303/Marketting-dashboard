import pytest
import pandas as pd
import numpy as np
import io
from app import app, calculate_kpis, parse_currency, validate_events_csv, validate_costs_csv, clean_and_validate_data


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_events_data():
    """Sample events CSV data"""
    return pd.DataFrame({
        'Campaign_ID': [1, 2, 3, 4, 5],
        'Channel_Used': ['Google Ads', 'Facebook', 'YouTube', 'Instagram', 'Email'],
        'Campaign_Type': ['Search', 'Social', 'Video', 'Social', 'Email'],
        'Company': ['TechCorp', 'RetailCo', 'TechCorp', 'RetailCo', 'TechCorp'],
        'Clicks': [100, 150, 200, 120, 80],
        'Impressions': [1000, 1500, 2000, 1200, 800],
        'Conversion_Rate': [0.1, 0.15, 0.08, 0.12, 0.2],
        'Date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05'],
        'Acquisition_Cost': ['$100.00', '$150.50', '$200', '€120.75', '¥80']
    })


@pytest.fixture
def sample_costs_data():
    """Sample costs CSV data"""
    return pd.DataFrame({
        'campaign': [1, 2, 3, 4, 5],
        'channel': ['Google Ads', 'Facebook', 'YouTube', 'Instagram', 'Email'],
        'cpc': [1.0, 2.0, 1.5, 1.8, 0.5],
        'cpm': [10.0, 15.0, 12.0, 18.0, 5.0]
    })


class TestUtilityFunctions:
    """Test utility functions"""

    def test_parse_currency(self):
        """Test currency parsing function"""
        assert parse_currency('$100.00') == 100.0
        assert parse_currency('€150.50') == 150.5
        assert parse_currency('£200') == 200.0
        assert parse_currency('¥1,000') == 1000.0
        assert parse_currency('') == 0.0
        assert parse_currency(None) == 0.0
        assert parse_currency(np.nan) == 0.0
        assert parse_currency(100) == 100.0
        assert parse_currency('invalid') == 0.0

    def test_validate_events_csv(self, sample_events_data):
        """Test events CSV validation"""
        # Valid data
        is_valid, message = validate_events_csv(sample_events_data)
        assert is_valid is True
        assert message == "Valid"

        # Missing required column
        invalid_df = sample_events_data.drop(columns=['Campaign_ID'])
        is_valid, message = validate_events_csv(invalid_df)
        assert is_valid is False
        assert 'Campaign_ID' in message

    def test_validate_costs_csv(self, sample_costs_data):
        """Test costs CSV validation"""
        # Valid data
        is_valid, message = validate_costs_csv(sample_costs_data)
        assert is_valid is True
        assert message == "Valid"

        # Missing required column
        invalid_df = sample_costs_data.drop(columns=['cpc'])
        is_valid, message = validate_costs_csv(invalid_df)
        assert is_valid is False
        assert 'cpc' in message

    def test_clean_and_validate_data(self, sample_events_data):
        """Test data cleaning and validation"""
        cleaned_df = clean_and_validate_data(sample_events_data.copy())
        
        # Check if date column is parsed
        assert pd.api.types.is_datetime64_any_dtype(cleaned_df['Date'])
        
        # Check if acquisition cost is parsed
        assert 'Acquisition_Cost_Parsed' in cleaned_df.columns
        assert cleaned_df['Acquisition_Cost_Parsed'].iloc[0] == 100.0
        assert cleaned_df['Acquisition_Cost_Parsed'].iloc[1] == 150.5


class TestKPICalculations:
    """Test KPI calculation functions"""

    def test_calculate_kpis_basic(self, sample_events_data):
        """Test basic KPI calculations"""
        kpis = calculate_kpis(sample_events_data)
        
        # Views = sum of impressions
        expected_views = sample_events_data['Impressions'].sum()
        assert kpis['views'] == expected_views
        
        # Signups = sum of clicks
        expected_signups = sample_events_data['Clicks'].sum()
        assert kpis['signups'] == expected_signups
        
        # Purchases = sum of (clicks * conversion_rate) rounded
        expected_purchases = int((sample_events_data['Clicks'] * sample_events_data['Conversion_Rate']).round().sum())
        assert kpis['purchases'] == expected_purchases
        
        # Rates
        assert kpis['signup_view_rate'] > 0
        assert kpis['purchase_signup_rate'] > 0

    def test_calculate_kpis_with_costs(self, sample_events_data, sample_costs_data):
        """Test KPI calculations with costs CSV"""
        kpis = calculate_kpis(sample_events_data, sample_costs_data)
        
        # Should calculate CAC using costs CSV
        assert kpis['estimated_cac'] > 0

    def test_calculate_kpis_empty_data(self):
        """Test KPI calculations with empty data"""
        kpis = calculate_kpis(None)
        
        assert kpis['views'] == 0
        assert kpis['signups'] == 0
        assert kpis['purchases'] == 0
        assert kpis['signup_view_rate'] == 0.0
        assert kpis['purchase_signup_rate'] == 0.0
        assert kpis['estimated_cac'] == 0.0
        assert kpis['top_campaigns'] == []

    def test_calculate_kpis_top_campaigns(self, sample_events_data):
        """Test top campaigns calculation"""
        kpis = calculate_kpis(sample_events_data)
        
        # Should have top campaigns
        assert len(kpis['top_campaigns']) > 0
        
        # Each campaign should have required fields
        for campaign in kpis['top_campaigns']:
            assert 'Campaign_ID' in campaign
            assert 'Channel_Used' in campaign
            assert 'purchase_signup_rate' in campaign


class TestAPIRoutes:
    """Test API routes"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/healthz')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'data_loaded' in data

    def test_dashboard_json_no_data(self, client):
        """Test dashboard JSON endpoint with no data"""
        # Set up authenticated session
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        response = client.get('/dashboard.json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['views'] == 0
        assert data['signups'] == 0
        assert data['purchases'] == 0

    def test_dashboard_page(self, client):
        """Test dashboard page"""
        # Set up authenticated session
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        response = client.get('/')
        assert response.status_code == 200
        assert b'Marketing Insights Dashboard' in response.data

    def test_set_role_get(self, client):
        """Test set role page GET"""
        # Set up authenticated Admin session
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        response = client.get('/set-role')
        assert response.status_code == 200
        # Check for generic role management content
        assert b'role' in response.data.lower() or b'admin' in response.data.lower()

    def test_set_role_post(self, client):
        """Test set role page POST"""
        # Set up authenticated Admin session
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        response = client.post('/set-role', data={'role': 'Editor'}, follow_redirects=True)
        assert response.status_code == 200

    def test_upload_no_permission(self, client):
        """Test upload without proper permissions"""
        # Set up Viewer role (no upload permission)
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'viewer'
            sess['role'] = 'Viewer'
        
        response = client.post('/upload', data={})
        assert response.status_code == 403

    def test_upload_no_file(self, client):
        """Test upload without file"""
        # Set up authenticated Admin session
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        response = client.post('/upload', data={})
        assert response.status_code == 400

    def test_upload_valid_file(self, client, sample_events_data):
        """Test upload with valid file"""
        # Set up authenticated Admin session
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        # Convert DataFrame to CSV string
        csv_string = sample_events_data.to_csv(index=False)
        csv_file = io.BytesIO(csv_string.encode('utf-8'))
        
        data = {
            'events_csv': (csv_file, 'events.csv')
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        
        response_data = response.get_json()
        assert 'message' in response_data
        assert response_data['events_rows'] == len(sample_events_data)

    def test_upload_invalid_file(self, client):
        """Test upload with invalid file"""
        # Set up authenticated Admin session
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        # Create invalid CSV (missing required columns)
        invalid_csv = "col1,col2\n1,2\n3,4"
        csv_file = io.BytesIO(invalid_csv.encode('utf-8'))
        
        data = {
            'events_csv': (csv_file, 'events.csv')
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_division_by_zero_handling(self):
        """Test handling of division by zero in KPI calculations"""
        # Create data with zero impressions/clicks
        df = pd.DataFrame({
            'Campaign_ID': [1],
            'Channel_Used': ['Test'],
            'Campaign_Type': ['Search'],
            'Company': ['TestCorp'],
            'Clicks': [0],
            'Impressions': [0],
            'Conversion_Rate': [0.1],
            'Date': ['2021-01-01'],
            'Acquisition_Cost': ['$0.00']
        })
        
        kpis = calculate_kpis(df)
        
        # Should handle division by zero gracefully
        assert kpis['signup_view_rate'] == 0.0
        assert kpis['purchase_signup_rate'] == 0.0

    def test_malformed_data_handling(self):
        """Test handling of malformed data"""
        # Create data with NaN values
        df = pd.DataFrame({
            'Campaign_ID': [1, 2],
            'Channel_Used': ['Test1', 'Test2'],
            'Campaign_Type': ['Search', 'Social'],
            'Company': ['Corp1', 'Corp2'],
            'Clicks': [100, None],  # NaN value
            'Impressions': [1000, 2000],
            'Conversion_Rate': [0.1, 0.2],
            'Date': ['2021-01-01', '2021-01-02'],
            'Acquisition_Cost': ['$100.00', '$200.00']
        })
        
        try:
            cleaned_df = clean_and_validate_data(df)
            kpis = calculate_kpis(cleaned_df)
            # Should not crash
            assert isinstance(kpis, dict)
        except Exception as e:
            # Should handle gracefully
            assert "Invalid" in str(e) or "Error" in str(e) or "Column" in str(e)

    def test_large_dataset_performance(self):
        """Test performance with larger dataset"""
        # Create larger dataset
        large_df = pd.DataFrame({
            'Campaign_ID': list(range(1000)),
            'Channel_Used': ['Channel'] * 1000,
            'Campaign_Type': ['Search'] * 1000,
            'Company': ['TestCorp'] * 1000,
            'Clicks': [100] * 1000,
            'Impressions': [1000] * 1000,
            'Conversion_Rate': [0.1] * 1000,
            'Date': ['2021-01-01'] * 1000,
            'Acquisition_Cost': ['$100.00'] * 1000
        })
        
        # Should handle large dataset without issues
        kpis = calculate_kpis(large_df)
        assert kpis['views'] == 1000000  # 1000 * 1000
        assert kpis['signups'] == 100000  # 1000 * 100


if __name__ == '__main__':
    pytest.main(['-v', '--cov=app', '--cov-report=xml', '--cov-report=term-missing'])
