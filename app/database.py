from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.config.config import Config

db = SQLAlchemy()

engine = create_engine(Config.DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)