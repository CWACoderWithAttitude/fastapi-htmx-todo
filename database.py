# https://medium.com/towards-data-engineering/fastapi-with-sql-1c7852ccbf21
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
DB_URL = "sqlite:///./test.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
