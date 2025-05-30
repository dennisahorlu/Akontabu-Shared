from app import app
from extensions import db
from models import User, Product, Sale, Payment

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Optional: Add initial test data
    if not User.query.first():
        test_user = User(
            name="Test User",
            email="test@example.com",
            business_name="Test Business"
        )
        test_user.set_password("password")
        db.session.add(test_user)
        db.session.commit()