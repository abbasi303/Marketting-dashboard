import os
import tempfile
import pytest
from app import create_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    # Create a temporary file to isolate the instance for tests
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'UPLOAD_FOLDER': tempfile.mkdtemp(),
    })

    # Create an app context
    with app.app_context():
        pass  # We would initialize the database here if we had one

    yield app

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner()


@pytest.fixture
def mock_processed_data(app):
    """Create mock processed data for testing"""
    import json
    import os
    
    # Define mock data
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
            }
        ],
        "channel_performance": [
            {
                "channel": "Social Media",
                "roi": 175.3,
                "conversion_rate": 23.7,
                "acquisition_cost": 12.50
            }
        ],
        "cac": [
            {
                "channel": "Email",
                "roi": 230.1,
                "conversion_rate": 28.4,
                "acquisition_cost": 5.20
            }
        ]
    }
    
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.join(app.instance_path, 'data'), exist_ok=True)
    
    # Write mock data to the processed_data.json file
    with open(os.path.join(app.instance_path, 'data', 'processed_data.json'), 'w') as f:
        json.dump(mock_data, f)
    
    # Create the flag file
    with open(os.path.join(app.instance_path, 'data', 'initial_load_complete'), 'w') as f:
        f.write('done')
    
    return mock_data


class AuthActions:
    """Helper class for authentication in tests"""
    
    def __init__(self, client):
        self._client = client
    
    def login(self, username='admin', password='adminpass'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )
    
    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """Authentication fixture"""
    return AuthActions(client)
