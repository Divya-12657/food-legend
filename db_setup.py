import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

Base.metadata.create_all(bind=engine)

# DATABASE_URL = 'postgresql://postgres:foodforthought@localhost:5432/postgres'

# DATABASE_URL = 'postgresql://postgres:foodforthought@172.31.36.216:5432/postgres'

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# Base.metadata.create_all(bind=engine)
print(Base.metadata.tables.keys())


from app.models import User, Donor,TokenBlacklist
