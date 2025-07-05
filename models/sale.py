from datetime import datetime
from extensions import db

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Selling price at time of sale
    profit = db.Column(db.Float)  # Calculated profit (price - cost_price) * quantity
    customer = db.Column(db.String(100))
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    def calculate_profit(self, product):
        """Calculate and store profit based on product cost"""
        if product:
            self.profit = round((self.price - product.cost_price) * self.quantity, 2)
            self.total_amount = round(self.price * self.quantity, 2)
        return self.profit
    
    @property
    def total_amount(self):
        return self.quantity * self.price