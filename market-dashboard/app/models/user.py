from flask_login import UserMixin
from app import login_manager


class User(UserMixin):
    """User class for authentication and authorization"""
    
    def __init__(self, username, role='viewer'):
        self.id = username
        self.username = username
        self.role = role  # 'admin', 'editor', or 'viewer'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_editor(self):
        return self.role == 'editor' or self.role == 'admin'
    
    @property
    def is_viewer(self):
        return True  # All roles can view


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    # In a real app, we would fetch from database
    # For demo purposes, we'll use hardcoded users
    from app.routes.auth import DEMO_USERS
    
    if user_id in DEMO_USERS:
        return User(user_id, DEMO_USERS[user_id]['role'])
    return None
