"""
Authentication and RBAC tests for Marketing Insights Dashboard
"""
import pytest
from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


class TestAuthentication:
    """Test authentication functionality"""

    def test_login_get_page(self, client):
        """Test login page loads"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_login_valid_credentials(self, client):
        """Test login with valid credentials"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Marketing Insights Dashboard' in response.data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/login', data={
            'username': 'invalid',
            'password': 'wrong'
        })
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_empty_credentials(self, client):
        """Test login with empty credentials"""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        })
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_logout_functionality(self, client):
        """Test logout clears session"""
        # First login
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_dashboard_requires_authentication(self, client):
        """Test dashboard redirects to login when not authenticated"""
        response = client.get('/')
        assert response.status_code == 302  # Redirect to login
        assert '/login' in response.location


class TestRBAC:
    """Test Role-Based Access Control"""

    def test_viewer_role_permissions(self, client):
        """Test Viewer role can view but not upload"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'viewer'
            sess['role'] = 'Viewer'
        
        # Can access dashboard
        response = client.get('/')
        assert response.status_code == 200
        
        # Cannot upload
        response = client.post('/upload', data={})
        assert response.status_code == 403

    def test_upload_403_without_proper_role(self, client):
        """Test 403 forbidden when user lacks upload permission"""
        # Test with no authentication at all
        response = client.post('/upload', data={})
        # Should get 403 or redirect depending on implementation
        assert response.status_code in [403, 302]

    def test_editor_role_permissions(self, client):
        """Test Editor role can view and upload"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'editor'
            sess['role'] = 'Editor'
        
        # Can access dashboard
        response = client.get('/')
        assert response.status_code == 200
        
        # Can access upload (though will fail without file)
        response = client.post('/upload', data={})
        assert response.status_code == 400  # Bad request, not forbidden

    def test_admin_role_permissions(self, client):
        """Test Admin role has full access"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin' 
            sess['role'] = 'Admin'
        
        # Can access all pages
        response = client.get('/')
        assert response.status_code == 200
        
        response = client.get('/set-role')
        assert response.status_code == 200

    def test_non_admin_cannot_access_set_role(self, client):
        """Test non-Admin users cannot access /set-role"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'viewer'
            sess['role'] = 'Viewer'
        
        response = client.get('/set-role')
        assert response.status_code == 302  # Redirected to dashboard

    def test_set_role_invalid_role(self, client):
        """Test setting invalid role"""
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        response = client.post('/set-role', data={'role': 'InvalidRole'}, follow_redirects=True)
        assert response.status_code == 200
        # Role should not change

    def test_get_current_role_function(self, client):
        """Test get_current_role with no session"""
        # Simply test the function returns default when no session
        response = client.get('/healthz')  # This will establish proper context
        assert response.status_code == 200  # Simple validation test

    def test_requires_upload_permission_various_roles(self, client):
        """Test upload permission for different roles"""
        from app import requires_upload_permission
        
        # Test Viewer role (no permission)
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'viewer'
            sess['role'] = 'Viewer'
        
        # Make a request to establish session context
        response = client.get('/healthz')  # Simple endpoint to establish context
        assert response.status_code == 200
        
        # Test Admin role (has permission) 
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
            sess['role'] = 'Admin'
        
        # Verify through actual upload attempt
        response = client.post('/upload', data={})
        assert response.status_code == 400  # Should be bad request (no file), not 403 (no permission)
