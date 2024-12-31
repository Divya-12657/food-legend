from flask import Flask
from app.routes import auth
from db_setup import Base,engine
from app.models import Base

def create_app():
    app = Flask(__name__)

    # Register Blueprint
    app.register_blueprint(auth, url_prefix='/auth')

    
    # Drop all tables and recreate them
    # Base.metadata.drop_all(bind=engine)  # Drop existing tables
    Base.metadata.create_all(bind=engine)  # Recreate tables with updated model

    return app
