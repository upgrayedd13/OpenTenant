from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from ..models.model_base import ModelBase
from ..config import Config


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
ModelBase.metadata.create_all(engine)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)