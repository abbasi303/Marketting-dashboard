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
