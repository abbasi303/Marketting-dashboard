import os
import pytest
from app.services.data_service import validate_csv, process_marketing_data, load_campaign_costs


class TestDataService:
    """Test the data service functions"""
    
    def test_validate_csv_events_valid(self, app):
        """Test validation of valid events CSV"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        file_path = os.path.join(data_dir, 'sample_events.csv')
        
        with app.app_context():
            result = validate_csv(file_path, 'events')
            
            assert result['valid'] is True
            assert 'errors' in result
            assert len(result['errors']) == 0
    
    def test_validate_csv_costs_valid(self, app):
        """Test validation of valid costs CSV"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        file_path = os.path.join(data_dir, 'sample_costs.csv')
        
        with app.app_context():
            result = validate_csv(file_path, 'costs')
            
            assert result['valid'] is True
            assert 'errors' in result
            assert len(result['errors']) == 0
    
    def test_validate_csv_events_invalid(self, app, tmpdir):
        """Test validation of invalid events CSV"""
        # Create an invalid CSV file
        invalid_file = tmpdir.join('invalid_events.csv')
        invalid_file.write('user_id,event,campaign,timestamp\n1001,view,Test,2025-01-01T10:00:00')
        
        with app.app_context():
            result = validate_csv(str(invalid_file), 'events')
            
            assert result['valid'] is False
            assert 'errors' in result
            assert len(result['errors']) > 0
            # Should have errors for missing columns and invalid event type
            assert any('channel' in error for error in result['errors'])
            assert any('event_type' in error for error in result['errors'])
    
    def test_validate_csv_costs_invalid(self, app, tmpdir):
        """Test validation of invalid costs CSV"""
        # Create an invalid CSV file
        invalid_file = tmpdir.join('invalid_costs.csv')
        invalid_file.write('campaign,channel,cost\n')
        
        with app.app_context():
            result = validate_csv(str(invalid_file), 'costs')
            
            assert result['valid'] is False
            assert 'errors' in result
            assert len(result['errors']) > 0
            # Should have errors for missing columns
            assert any('cpc' in error for error in result['errors'])
            assert any('cpm' in error for error in result['errors'])
    
    def test_process_marketing_data(self, app):
        """Test processing marketing data"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        file_path = os.path.join(data_dir, 'sample_events.csv')
        
        with app.app_context():
            result = process_marketing_data(file_path)
            
            # Check that we have the expected keys
            assert 'funnel' in result
            assert 'conversion_rates' in result
            assert 'campaign_performance' in result
            assert 'channel_performance' in result
            
            # Check funnel data
            assert result['funnel']['page_view'] > 0
            assert result['funnel']['signup'] > 0
            assert result['funnel']['purchase'] > 0
            
            # Check conversion rates
            assert result['conversion_rates']['signup_rate'] > 0
            assert result['conversion_rates']['purchase_rate'] > 0
            assert result['conversion_rates']['overall_conversion'] > 0
            
            # Check campaign performance
            assert len(result['campaign_performance']) > 0
            assert 'campaign' in result['campaign_performance'][0]
            assert 'signup_rate' in result['campaign_performance'][0]
            
            # Check channel performance
            assert len(result['channel_performance']) > 0
            assert 'channel' in result['channel_performance'][0]
            assert 'purchase_rate' in result['channel_performance'][0]
    
    def test_load_campaign_costs(self, app):
        """Test loading campaign costs"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        file_path = os.path.join(data_dir, 'sample_costs.csv')
        
        with app.app_context():
            result = load_campaign_costs(file_path)
            
            assert 'campaigns' in result
            assert 'channels' in result
            assert 'entries' in result
            
            assert result['campaigns'] > 0
            assert result['channels'] > 0
            assert result['entries'] > 0
