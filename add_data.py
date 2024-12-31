from app import create_app, db
from app.models import User  # Import the User model

app = create_app()

# Add data within the app context
with app.app_context():
    # Create all tables (if they don't exist)
    db.create_all()

    # Create multiple user instances
    user1 = User(username='alice', email='alice@example.com')
    user2 = User(username='bob', email='bob@example.com')

    # Add all users to the session at once
    db.session.add_all([user1, user2])

    # Commit the session to save the users to the database
    db.session.commit()

    print("Users added successfully!")
