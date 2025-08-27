import os
from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # 100MB max upload size
        ALLOWED_EXTENSIONS={'csv'},
        JSON_SORT_KEYS=False,  # Preserve key order in JSON responses
        JSONIFY_PRETTYPRINT_REGULAR=False,  # Don't pretty-print JSON in production
        SEND_FILE_MAX_AGE_DEFAULT=31536000  # Cache static files for 1 year
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        pass

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from app.routes import main, auth, api, analytics
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(analytics.analytics_blueprint)

    return app
