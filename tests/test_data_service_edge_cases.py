import pytest
import pandas as pd
import os
import tempfile
from app.services.data_service import process_marketing_data, validate_csv

def test_validate_csv_empty_file():
    """Test validation with empty file"""
    # Create a temporary empty file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        empty_file = f.name
        
    try:
        result = validate_csv(empty_file, 'campaign')
        assert not result['valid']
        assert 'errors' in result
    finally:
        # Clean up
        if os.path.exists(empty_file):
            os.remove(empty_file)

def test_validate_csv_missing_columns():
    """Test validation with missing required columns"""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        f.write(b"campaign,cost\nTestCampaign,500\n")
        test_csv = f.name
        
    try:
        result = validate_csv(test_csv, 'campaign')
        assert not result['valid']
        assert 'errors' in result
        assert any('missing required column' in error.lower() for error in result['errors'])
    finally:
        if os.path.exists(test_csv):
            os.remove(test_csv)

def test_process_data_zero_division_protection():
    """Test that processing handles zero division cases"""
    # Create a CSV with data that would cause zero division
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        f.write(b"campaign,impressions,clicks,conversions,cost\nTestCampaign,100,0,0,500\n")
        test_csv = f.name
        
    try:
        result = process_marketing_data(test_csv, 'campaign')
        # Should handle zero division gracefully
        assert result is not None
        # Specifically check conversion rates - should be 0, not error
        assert 'conversion_rates' in result
        assert result['conversion_rates']['click_through_rate'] == 0
    finally:
        if os.path.exists(test_csv):
            os.remove(test_csv)

def test_process_data_with_invalid_numbers():
    """Test processing handles invalid numbers"""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        f.write(b"campaign,impressions,clicks,conversions,cost\nTestCampaign,invalid,10,5,500\n")
        test_csv = f.name
        
    try:
        # Should not raise exception but handle gracefully
        result = process_marketing_data(test_csv, 'campaign')
        assert 'error' in result
    except Exception as e:
        pytest.fail(f"Processing invalid data raised exception: {e}")
    finally:
        if os.path.exists(test_csv):
            os.remove(test_csv)
