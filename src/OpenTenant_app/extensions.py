from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy import MetaData

# while we'll generally use ORM models, we'll also include a MetaData object for arbitrary reflection
db = SQLAlchemy()
md = MetaData()

migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "account.login"
