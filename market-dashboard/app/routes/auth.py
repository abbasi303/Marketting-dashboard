from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

# For demo purposes, we'll use these predefined users
# In a real application, we would use a database
DEMO_USERS = {
    'admin': {
        'password': generate_password_hash('adminpass'),
        'role': 'admin'
    },
    'editor': {
        'password': generate_password_hash('editorpass'),
        'role': 'editor'
    },
    'viewer': {
        'password': generate_password_hash('viewerpass'),
        'role': 'viewer'
    }
}


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif username not in DEMO_USERS:
            error = 'Invalid username.'
        elif not check_password_hash(DEMO_USERS[username]['password'], password):
            error = 'Invalid password.'

        if error is None:
            # Create a User object
            user = User(username, DEMO_USERS[username]['role'])
            login_user(user)
            return redirect(url_for('main.index'))

        flash(error, 'error')

    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    logout_user()
    return redirect(url_for('auth.login'))
