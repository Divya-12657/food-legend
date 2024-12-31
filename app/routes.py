# from flask import Blueprint, request, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy.orm import Session
# from db_setup import SessionLocal
# from app.models import User, Donor
# from datetime import datetime



# auth = Blueprint('auth', __name__)

# # Dependency to get the database session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Signup Endpoint
# @auth.route('/signup', methods=['POST'])
# def signup():
#     db = next(get_db())
#     data = request.get_json()

#     if not data.get('username') or not data.get('email') or not data.get('password'):
#         return jsonify({"error": "Missing fields"}), 400

#     if db.query(User).filter(User.email == data['email']).first():
#         return jsonify({"error": "User already exists"}), 400

#     hashed_password = generate_password_hash(data['password'])

#     new_user = User(
#         username=data['username'],
#         email=data['email'],
#         password=hashed_password
#     )
#     db.add(new_user)
#     db.commit()
#     return jsonify({"message": "User created successfully"}), 201

# # Login Endpoint
# @auth.route('/login', methods=['POST'])
# def login():
#     db = next(get_db())
#     data = request.get_json()

#     if not data.get('email') or not data.get('password'):
#         return jsonify({"error": "Missing fields"}), 400

#     user = db.query(User).filter(User.email == data['email']).first()
#     if not user or not check_password_hash(user.password, data['password']):
#         return jsonify({"error": "Invalid credentials"}), 401

#     return jsonify({"message": f"Welcome, {user.username}!"}), 200


# @auth.route('/donate', methods=['POST'])
# def post_donation():
#     db = next(get_db())
#     data = request.get_json()

#     # # Validate required fields
#     # if not data.get('food_type') or not data.get('quantity') or not data.get('location'):
#     #     return jsonify({"error": "Missing required fields (food_type, quantity, location)"}), 400

#     # Ensure user_id is present
#     user_id = data.get('user_id')
#     if not user_id:
#         return jsonify({"error": "User ID is required"}), 400

#     # Check if user exists
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     # Create donor entry
#     donor = Donor(
#         user_id=user_id,
#         food_type=data['food_type'],
#         quantity=data['quantity'],
#         location=data['location'],
#         status="available" # Default status is "available"
#         # created_at=datetime.utcnow(),
#         # updated_at=datetime.utcnow()
#     )

#     # Add to DB and commit
#     db.add(donor)
#     db.commit()

#     return jsonify({"message": "Food availability posted successfully", "donor_id": donor.id}), 201


# JWT token login/
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db_setup import SessionLocal
from app.models import User, Donor
from functools import wraps
import os
from sqlalchemy import select  # Import select function

auth = Blueprint('auth', __name__)

# Secret Key for JWT Encoding/Decoding
SECRET_KEY = os.getenv("SECRET_KEY", "123456789abcdbegrt")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to verify JWT token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db = next(get_db())  # Get the db session here
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Get token from header
        if not token:
            return jsonify({'error': 'Token is missing!'}), 403
        try:
            # Decode the token and print for debugging
            print(f"Decoding token: {token}")
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(f"Decoded data: {data}")

            # Use SQLAlchemy 2.x select method to query the user
            stmt = select(User).filter_by(id=data['user_id'])
            current_user = db.execute(stmt).scalars().first()  # Execute the statement and fetch the result
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function

@auth.route('/')
def home():
    return "Welcome to the Home Page!"


# Signup Endpoint
@auth.route('/signup', methods=['POST'])
def signup():
    db = next(get_db())
    data = request.get_json()

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing fields"}), 400

    stmt = select(User).filter(User.email == data['email'])
    user = db.execute(stmt).scalars().first()
    if user:
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(data['password'])

    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    return jsonify({"message": "User created successfully"}), 201

# Login Endpoint
@auth.route('/login', methods=['POST'])
def login():
    db = next(get_db())
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing fields"}), 400

    # Use SQLAlchemy 2.x style query with select
    stmt = select(User).filter(User.email == data['email'])
    user = db.execute(stmt).scalars().first()  # .scalars() is used to extract a single result

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Expiration time (1 hour)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"message": f"Welcome, {user.username}!", "token": token}), 200

# Donor Donation Endpoint (protected)
@auth.route('/donate', methods=['POST'])
@token_required
def post_donation(current_user):
    db = next(get_db())
    data = request.get_json()

    user_id = data.get('user_id')
    if not user_id or user_id != current_user.id:
        return jsonify({"error": "User ID is invalid or does not match the token"}), 400

    stmt = select(User).filter(User.id == user_id)
    user = db.execute(stmt).scalars().first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    donor = Donor(
        user_id=user_id,
        food_type=data['food_type'],
        quantity=data['quantity'],
        location=data['location'],
        status="available"
    )

    db.add(donor)
    db.commit()

    return jsonify({"message": "Food availability posted successfully", "donor_id": donor.id}), 201
