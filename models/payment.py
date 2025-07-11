from datetime import datetime
from extensions import db
import math


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Common fields
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))

    # Product-specific fields
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    base_cost = db.Column(db.Float) 
    transportation = db.Column(db.Float)
    carriage = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    cost_per_unit = db.Column(db.Float)
    profit_margin = db.Column(db.Float)
    selling_price = db.Column(db.Float)

    def calculate_selling_price(self):
        def round_up_to_nearest_half(value):
            return math.ceil(value * 2) / 2

        if self.payment_type == 'product':
            self.total_cost = (self.base_cost or 0) + (self.transportation or 0) + (self.carriage or 0)

            if self.quantity and self.total_cost and self.profit_margin is not None:
                self.cost_per_unit = self.base_cost / self.quantity
                self.selling_price = round_up_to_nearest_half(self.cost_per_unit * (1 + (self.profit_margin / 100)))
                self.amount = self.total_cost

    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
        self.calculate_selling_price()

    def __repr__(self):
        return f"<Payment {self.id}: {self.payment_type} - GHS {self.amount}>"
