# Quick script to generate test data
import os
import json
from pathlib import Path

# Define our mock data
mock_data = {
    "funnel": {
        "impressions": 100000,
        "clicks": 20000,
        "conversions": 5000
    },
    "conversion_rates": {
        "click_through_rate": 20.0,
        "conversion_rate": 25.0,
        "roi": 150.0
    },
    "campaign_performance": [
        {
            "campaign_name": "Summer Sale 2025",
            "roi": 180.5,
            "conversion_rate": 27.3,
            "cost": 12000,
            "revenue": 33600
        },
        {
            "campaign_name": "New Customer Promo",
            "roi": 135.2,
            "conversion_rate": 19.8,
            "cost": 8500,
            "revenue": 20000
        },
        {
            "campaign_name": "Back to School",
            "roi": 95.7,
            "conversion_rate": 15.3,
            "cost": 10000,
            "revenue": 19570
        },
        {
            "campaign_name": "Holiday Special",
            "roi": 210.3,
            "conversion_rate": 32.5,
            "cost": 15000,
            "revenue": 46545
        }
    ],
    "channel_performance": [
        {
            "channel": "Social Media",
            "roi": 175.3,
            "conversion_rate": 23.7,
            "acquisition_cost": 12.50
        },
        {
            "channel": "Email",
            "roi": 230.1,
            "conversion_rate": 28.4,
            "acquisition_cost": 5.20
        },
        {
            "channel": "Search",
            "roi": 160.8,
            "conversion_rate": 18.9,
            "acquisition_cost": 15.75
        },
        {
            "channel": "Display",
            "roi": 95.6,
            "conversion_rate": 10.2,
            "acquisition_cost": 25.30
        },
        {
            "channel": "Affiliate",
            "roi": 120.4,
            "conversion_rate": 15.8,
            "acquisition_cost": 18.90
        }
    ],
    "cac": [
        {
            "channel": "Social Media",
            "roi": 175.3,
            "conversion_rate": 23.7,
            "acquisition_cost": 12.50
        },
        {
            "channel": "Email",
            "roi": 230.1,
            "conversion_rate": 28.4,
            "acquisition_cost": 5.20
        },
        {
            "channel": "Search",
            "roi": 160.8,
            "conversion_rate": 18.9,
            "acquisition_cost": 15.75
        },
        {
            "channel": "Display",
            "roi": 95.6,
            "conversion_rate": 10.2,
            "acquisition_cost": 25.30
        },
        {
            "channel": "Affiliate",
            "roi": 120.4,
            "conversion_rate": 15.8,
            "acquisition_cost": 18.90
        },
        {
            "channel": "Direct",
            "roi": 140.2,
            "conversion_rate": 30.5,
            "acquisition_cost": 8.75
        },
        {
            "channel": "Referral",
            "roi": 195.8,
            "conversion_rate": 35.2,
            "acquisition_cost": 6.30
        }
    ]
}

def create_test_data():
    # Get the instance path where data should be stored
    base_dir = Path(__file__).parent.parent  # Go up two levels from this script
    instance_dir = base_dir / 'instance'
    data_dir = instance_dir / 'data'
    
    # Create directories if they don't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Write the mock data
    data_path = data_dir / 'processed_data.json'
    with open(data_path, 'w') as f:
        json.dump(mock_data, f, indent=2)
    
    # Create the flag file to indicate data is available
    flag_path = data_dir / 'initial_load_complete'
    with open(flag_path, 'w') as f:
        f.write('done')
    
    print(f"Test data created at {data_path}")
    print(f"Flag file created at {flag_path}")

if __name__ == '__main__':
    create_test_data()
