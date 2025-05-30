from datetime import datetime
from extensions import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_type = db.Column(db.String(50), nullable=False)  # product, transportation, etc.
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # For product purchases
    product_name = db.Column(db.String(100))  # Added for direct product reference
    quantity = db.Column(db.Integer)
    total_cost = db.Column(db.Float)  # Changed from unit_cost to total_cost
    profit_margin = db.Column(db.Float)  # Added to store margin
    calculated_price = db.Column(db.Float)  # Added to store calculated selling price
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)


    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
    
        if self.payment_type == 'product':
            if not kwargs.get('amount') and self.total_cost:
                self.amount = self.total_cost
            
            if self.total_cost and self.profit_margin and not kwargs.get('calculated_price'):
                self.calculated_price = self.total_cost * (1 + self.profit_margin / 100)

    def __repr__(self):
        return f"<Payment {self.id} - {self.payment_type} - ${self.amount}>"
