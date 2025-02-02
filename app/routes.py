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
from app.models import User, Donor,TokenBlacklist
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

# # Helper function to verify JWT token
# def token_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         db = next(get_db())  # Get the db session here
#         token = None
#         if 'Authorization' in request.headers:
#             token = request.headers['Authorization'].split(" ")[1]  # Get token from header
#         if not token:
#             return jsonify({'error': 'Token is missing!'}), 403
#         try:
#             # Decode the token and print for debuggin
#             print(f"Decoding token: {token}")
#             data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#             print(f"Decoded data: {data}")

#             # Use SQLAlchemy 2.x select method to query the user
#             stmt = select(User).filter_by(id=data['user_id'])
#             current_user = db.execute(stmt).scalars().first()  # Execute the statement and fetch the result
#         except jwt.ExpiredSignatureError:
#             return jsonify({'error': 'Token has expired!'}), 403
#         except jwt.InvalidTokenError:
#             return jsonify({'error': 'Token is invalid!'}), 403
#         return f(current_user, *args, **kwargs)
#     return decorated_function

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db = next(get_db())
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Extract the token
        if not token:
            return jsonify({'error': 'Token is missing!'}), 403

        # Check if the token is blacklisted
        blacklisted_token = db.query(TokenBlacklist).filter_by(token=token).first()
        if blacklisted_token:
            return jsonify({'error': 'Token has been blacklisted. Please log in again.'}), 403

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            stmt = select(User).filter_by(id=data['user_id'])
            current_user = db.execute(stmt).scalars().first()
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
        password=hashed_password,
        role=data['role']
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

# Fetch all the food available (protected)
@auth.route('/available-orders', methods=['GET'])
@token_required
def get_available_orders(current_user):
    db = next(get_db())

    try:
        # Check the role of the current user
        if current_user.role == 'donor':
            # Donors should see only their own available orders
            stmt = select(Donor).filter(Donor.status == "available", Donor.user_id == current_user.id)
        elif current_user.role == 'receiver':
            # Receivers should see all available orders
            stmt = select(Donor).filter(Donor.status == "available")
        else:
            return jsonify({"error": "Unauthorized role"}), 403

        # Execute the query
        available_orders = db.execute(stmt).scalars().all()

        # Serialize the results
        orders_list = [
            {
                "id": order.id,
                "user_id": order.user_id,
                "food_type": order.food_type,
                "quantity": order.quantity,
                "location": order.location,
                "status": order.status,
            }
            for order in available_orders
        ]

        return jsonify({"available_orders": orders_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@auth.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    db = next(get_db())
    token = request.headers.get('Authorization', '').split(" ")[1]

    try:
        # Check if the token is already blacklisted
        blacklisted_token = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
        
        if blacklisted_token:
            return jsonify({'error': 'Token has been blacklisted. Please log in again.'}), 403
        
        # Add the token to the blacklist
        blacklisted_token = TokenBlacklist(token=token)
        db.add(blacklisted_token)
        db.commit()
        
        # Return success message
        return jsonify({"message": "You have been logged out successfully."}), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500


@auth.route('/generate-upi-link', methods=['POST'])
@token_required
def generate_upi_link(current_user):
    """
    Generate a dynamic UPI payment link for a donation or specific purpose.
    """
    data = request.get_json()

    # Required fields for generating the UPI link
    payee_vpa = data.get('payee_vpa')  # e.g., "recipient_vpa@upi"
    payee_name = data.get('payee_name')  # e.g., "Recipient Name"
    amount = data.get('amount')  # e.g., "100.50"
    order_id = data.get('order_id')  # Unique order ID
    notes = data.get('notes', "Donation")  # Optional notes

    if not payee_vpa or not payee_name or not amount or not order_id:
        return jsonify({"error": "Missing required fields: payee_vpa, payee_name, amount, order_id"}), 400

    # Generate the UPI link
    upi_link = (
        f"upi://pay?pa={payee_vpa}&pn={payee_name}&mc=&tid={order_id}&tr={order_id}"
        f"&tn={notes}&am={amount}&cu=INR"
    )

    return jsonify({"upi_link": upi_link}), 200