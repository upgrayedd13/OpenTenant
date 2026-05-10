from dotenv import load_dotenv
load_dotenv()

from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, jsonify
import logging
import os

from .config import DevelopmentConfig, ProductionConfig
from .extensions import db, login_manager, migrate

from .resources.routes import resources_bp
from .account.routes import account_bp
from .admin.routes import admin_bp
from .about.routes import about_bp
from .main.routes import main_bp


def create_app() -> None:
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Setup the configs depending on our selected environment type
    env = os.getenv("ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Ensure the upload directories exist
    os.makedirs(app.config['TMP_DIR'], exist_ok=True)
    os.makedirs(app.config['LEASES_DIR'], exist_ok=True)
    os.makedirs(app.config['FILE_REPOSITORY_DIR'], exist_ok=True)

    # Initialize the DB and app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(resources_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(main_bp)

    # Add a handler for requests that exceed the MAX_CONTENT_LENGTH
    @app.errorhandler(RequestEntityTooLarge)
    def request_too_large(e):
        return jsonify({'error': 'Request too large'}), 413

    # Add an endpoint so the JS can get configs from our .env
    @app.route('/config', methods=['GET'])
    def config():
        return jsonify({
            'maxUploadBytes': app.config['MAX_CONTENT_LENGTH']
        })

    # Log that we're done with setup
    logger = logging.getLogger(__name__)
    logger.info('App created!')
    return app
