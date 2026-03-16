from flask import Flask
import os

from .config import DevelopmentConfig, ProductionConfig
from .extensions import db, login_manager

from .account.routes import account_bp
from .admin.routes import admin_bp
from .info.routes import info_bp
from .main.routes import main_bp


def create_app() -> None:
    app = Flask(__name__)
    app.config.from_prefixed_env()

    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(info_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app