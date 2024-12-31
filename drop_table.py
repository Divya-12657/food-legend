from sqlalchemy import create_engine, text

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual database connection URL
engine = create_engine('postgresql://postgres:foodforthought@localhost:5432/postgres')

# Drop the table using raw SQL
with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS food_app.donors CASCADE"))