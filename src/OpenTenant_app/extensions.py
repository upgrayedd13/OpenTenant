from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from .models.model_base import ModelBase


db = SQLAlchemy(model_class=ModelBase)

migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "account.login"
