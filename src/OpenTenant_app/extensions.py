from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy import MetaData

from .models.model_base import ModelBase


db = SQLAlchemy(model_class=ModelBase)

# while we'll generally use ORM models, we'll also include a MetaData object for arbitrary reflection
md = MetaData()

migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "account.login"
