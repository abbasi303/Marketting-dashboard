import pytest
from app.models.user import User


def test_user_model():
    """Test the User model"""
    # Test admin user
    admin = User('admin', 'admin')
    assert admin.id == 'admin'
    assert admin.username == 'admin'
    assert admin.role == 'admin'
    assert admin.is_admin is True
    assert admin.is_editor is True
    assert admin.is_viewer is True
    
    # Test editor user
    editor = User('editor', 'editor')
    assert editor.id == 'editor'
    assert editor.username == 'editor'
    assert editor.role == 'editor'
    assert editor.is_admin is False
    assert editor.is_editor is True
    assert editor.is_viewer is True
    
    # Test viewer user
    viewer = User('viewer', 'viewer')
    assert viewer.id == 'viewer'
    assert viewer.username == 'viewer'
    assert viewer.role == 'viewer'
    assert viewer.is_admin is False
    assert viewer.is_editor is False
    assert viewer.is_viewer is True
