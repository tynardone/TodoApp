from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQL_ALCHEMY_DATABASE = (
#     "postgresql://tylernardone:test1234!@localhost/TodoApplicationDatabase"
# )

SQL_ALCHEMY_DATABASE = "sqlite:///./TodoApp.db"

engine = create_engine(SQL_ALCHEMY_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
