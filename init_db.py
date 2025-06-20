from app import app
from extensions import db
from models import User, Product, Sale, Payment, dashboard
from datetime import datetime



# class OtherPayment(db.Model):
#     __tablename__ = 'other_payments'

#     id = db.Column(db.Integer, primary_key=True)
#     category = db.Column(db.String(100), nullable=False)  # e.g., Rent, Utilities
#     amount = db.Column(db.Float, nullable=False)
#     description = db.Column(db.String(255))
#     date = db.Column(db.DateTime, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#     user = db.relationship('User', backref='other_payments')




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