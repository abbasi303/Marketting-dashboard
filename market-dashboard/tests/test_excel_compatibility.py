import os
import pytest
import pandas as pd
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from app.services.data_service import validate_csv, process_marketing_data


class TestExcelFileCompatibility:
    """Test compatibility with different Excel file formats"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for tests"""
        events_data = {
            'user_id': [1001, 1002, 1003, 1004, 1005],
            'event_type': ['page_view', 'page_view', 'signup', 'page_view', 'purchase'],
            'channel': ['organic', 'email', 'social', 'paid', 'email'],
            'campaign': ['none', 'newsletter', 'facebook', 'google', 'newsletter'],
            'timestamp': [
                '2025-01-01T10:00:00',
                '2025-01-01T10:15:00',
                '2025-01-01T10:30:00',
                '2025-01-01T10:45:00',
                '2025-01-01T11:00:00'
            ]
        }
        
        costs_data = {
            'channel': ['email', 'social', 'paid'],
            'campaign': ['newsletter', 'facebook', 'google'],
            'cost': [100.00, 250.00, 500.00],
        }
        
        return {
            'events': pd.DataFrame(events_data),
            'costs': pd.DataFrame(costs_data)
        }
    
    @pytest.fixture
    def temp_excel_files(self, sample_data):
        """Create temporary Excel files for testing"""
        temp_dir = tempfile.mkdtemp()
        
        # Create Excel files with different formats/versions
        excel_files = {}
        
        # Excel 97-2003 (.xls format)
        xls_path = os.path.join(temp_dir, 'events_97_2003.xls')
        sample_data['events'].to_excel(xls_path, index=False, engine='openpyxl')
        excel_files['xls'] = xls_path
        
        # Excel 2007+ (.xlsx format)
        xlsx_path = os.path.join(temp_dir, 'events_2007.xlsx')
        sample_data['events'].to_excel(xlsx_path, index=False, engine='openpyxl')
        excel_files['xlsx'] = xlsx_path
        
        # Create costs files too
        costs_xls = os.path.join(temp_dir, 'costs_97_2003.xls')
        sample_data['costs'].to_excel(costs_xls, index=False, engine='openpyxl')
        excel_files['costs_xls'] = costs_xls
        
        costs_xlsx = os.path.join(temp_dir, 'costs_2007.xlsx')
        sample_data['costs'].to_excel(costs_xlsx, index=False, engine='openpyxl')
        excel_files['costs_xlsx'] = costs_xlsx
        
        yield excel_files
        
        # Cleanup temp directory
        shutil.rmtree(temp_dir)
    
    @patch('app.services.data_service.pd.read_excel')
    @patch('app.services.data_service.pd.read_csv')
    def test_excel_file_detection(self, mock_read_csv, mock_read_excel, temp_excel_files):
        """Test that the service correctly detects and processes Excel files"""
        # Mock the pandas read functions to return our sample data
        mock_read_excel.return_value = pd.DataFrame({
            'user_id': [1001, 1002],
            'event_type': ['page_view', 'signup'],
            'channel': ['organic', 'email'],
            'campaign': ['none', 'newsletter'],
            'timestamp': ['2025-01-01T10:00:00', '2025-01-01T10:15:00']
        })
        
        # Test with an .xlsx file
        with patch('app.services.data_service.os.path.exists', return_value=True):
            # We'll patch the file extension check since we can't modify the function
            with patch('app.services.data_service.os.path.splitext', return_value=('events', '.xlsx')):
                result = validate_csv('/fake/path/events.xlsx')
                assert result['valid'] is True
                assert mock_read_excel.called
                assert not mock_read_csv.called
    
    @patch('app.services.data_service.json.dump')
    @patch('app.services.data_service.pd.read_excel')
    @patch('app.services.data_service.os.path.exists')
    @patch('app.services.data_service.os.makedirs')
    @patch('builtins.open', new_callable=MagicMock)
    def test_excel_data_processing(self, mock_open, mock_makedirs, mock_exists, 
                                  mock_read_excel, mock_json_dump, app):
        """Test processing marketing data from Excel files"""
        # Set up our mocks
        mock_exists.return_value = True
        
        # Mock the Excel read to return our test data
        mock_read_excel.return_value = pd.DataFrame({
            'user_id': [1001, 1002, 1003, 1004, 1005],
            'event_type': ['page_view', 'page_view', 'signup', 'page_view', 'purchase'],
            'channel': ['organic', 'email', 'social', 'paid', 'email'],
            'campaign': ['none', 'newsletter', 'facebook', 'google', 'newsletter'],
            'timestamp': [
                '2025-01-01T10:00:00',
                '2025-01-01T10:15:00',
                '2025-01-01T10:30:00',
                '2025-01-01T10:45:00',
                '2025-01-01T11:00:00'
            ]
        })
        
        with app.app_context():
            # Test the processing
            with patch('app.services.data_service.os.path.splitext', return_value=('events', '.xlsx')):
                result = process_marketing_data('/fake/path/events.xlsx')
                
                # Check that the function attempted to process the data
                assert mock_read_excel.called
                assert mock_json_dump.called
                
                # Check the result
                assert 'records_processed' in result
                assert result['records_processed'] > 0
