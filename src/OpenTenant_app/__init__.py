from dotenv import load_dotenv
load_dotenv()

from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, Response
import os

from .config import DevelopmentConfig, ProductionConfig
from .extensions import db, login_manager

from .account.routes import account_bp
from .admin.routes import admin_bp
from .info.routes import info_bp
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

    # Initialize the DB and app
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(info_bp)
    app.register_blueprint(main_bp)

    # Add security headers to harden the app
    @app.after_request
    def set_security_headers(response: Response) -> Response:
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'

        # Prevent content sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Enable HSTS (HTTPS only; adjust max-age as needed)
        # TODO: add this once HTTPS is working
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Basic Content Security Policy
        # TODO: We should probably add this back, but expand it (for dev purposes, leave out for now)
        # response.headers['Content-Security-Policy'] = (
        #     "default-src 'self'; "
        #     "script-src 'self'; "  
        #     "style-src 'self' 'unsafe-inline'; "
        #     "img-src 'self' data:;"
        # )

        return response

    # Create the DB tables that don't exist
    with app.app_context():
        db.create_all()

    return app
