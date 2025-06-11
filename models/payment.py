# # from datetime import datetime
# # from extensions import db
# # from sqlalchemy import Column, Integer, Float, String


# # class Payment(db.Model):
# #     __tablename__ = 'payments'
    
# #     id = db.Column(db.Integer, primary_key=True)
# #     payment_type = db.Column(db.String(50), nullable=False)  # product, transportation, etc.
# #     amount = db.Column(db.Float, nullable=False)
# #     description = db.Column(db.String(200))
    
    
# #     # For product purchases
# #     id = db.Column(db.Integer, primary_key=True)
# #     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
# #     product_name = Column(String(100), nullable=False)
# #     quantity = Column(Integer, nullable=False)
# #     base_cost = Column(Float, nullable=False)  # Original total cost without extras
# #     transportation = Column(Float, nullable=False)
# #     carriage = Column(Float, nullable=False)
# #     total_cost = Column(Float, nullable=False)  # This will now be base_cost + transportation + carriage
# #     cost_per_unit = Column(Float, nullable=False)
# #     profit_margin = Column(Float, nullable=False)
# #     selling_price = Column(Float, nullable=False)
# #     amount = Column(Float, nullable=False)
# #     description = Column(String(255))
    
# #     # Foreign Keys
# #     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
# #     product_id = db.Column(db.Integer, db.ForeignKey('products.id'), index=True)
# #     date = db.Column(db.DateTime, default=datetime.utcnow, index=True)


# #     def calculate_price(self):
# #         if self.total_cost is not None and self.profit_margin is not None:
# #             self.calculated_price = (self.total_cost + (self.transportation or 0) + (self.carriage or 0)) * (1 + self.profit_margin / 100)
# #             self.amount = self.amount or self.total_cost


# #     def __init__(self, **kwargs):
# #         super(Payment, self).__init__(**kwargs)
    
# #         if self.payment_type == 'product':
# #             self.calculate_price()
           
# #     def __repr__(self):
# #         if self.payment_type == 'product':
# #             return f"<Payment {self.id} - Product: {self.product_name} - ${self.amount}>"
# #         return f"<Payment {self.id} - {self.payment_type} - ${self.amount}>"

# # 

# from datetime import datetime
# from extensions import db

# class Payment(db.Model):
#     __tablename__ = 'payments'
    
#     id = db.Column(db.Integer, primary_key=True)
#     payment_type = db.Column(db.String(50), nullable=False)
#     amount = db.Column(db.Float, nullable=False)
#     description = db.Column(db.String(255))
#     date = db.Column(db.DateTime, default=datetime.utcnow)
    
#     # Product-specific fields
#     # class Payment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, nullable=False)
#     product_name = db.Column(db.String(100), nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)
#     base_cost = db.Column(db.Float, nullable=False)
#     transportation = db.Column(db.Float, nullable=False)
#     carriage = db.Column(db.Float, nullable=False)
#     profit_margin = db.Column(db.Float, nullable=False)
#     selling_price = db.Column(db.Float, nullable=False)
#     payment_type = db.Column(db.String(20), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
#     # Foreign keys
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

#     def calculate_costs(self):
#         if self.payment_type == 'product':
#             self.total_cost = (self.base_cost or 0) + (self.transportation or 0) + (self.carriage or 0)
#             if self.quantity and self.total_cost:
#                 self.cost_per_unit = self.total_cost / self.quantity
#                 self.selling_price = self.cost_per_unit * (1 + (self.profit_margin/100)) if self.profit_margin else 0
#                 self.amount = self.total_cost

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.calculate_costs()

#     def __repr__(self):
#         return f"<Payment {self.id}: {self.payment_type} - {self.amount}>"

from datetime import datetime
from extensions import db
from sqlalchemy import Column, Integer, Float, String
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
    base_cost = db.Column(db.Float)  # Product cost without extras
    transportation = db.Column(db.Float)
    carriage = db.Column(db.Float)
    total_cost = db.Column(db.Float)  # base_cost + transportation + carriage
    cost_per_unit = db.Column(db.Float)
    profit_margin = db.Column(db.Float)
    selling_price = db.Column(db.Float)
   # product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    
    def calculate_selling_price(self):
        def round_up_to_nearest_half(value):
            return math.ceil(value * 2) / 2

        if self.payment_type == 'product':
            # Calculate total cost including extras
            self.total_cost = (self.base_cost or 0) + (self.transportation or 0) + (self.carriage or 0)
            
            # Calculate selling price per unit
            if self.quantity and self.total_cost and self.profit_margin is not None:
                self.cost_per_unit = self.total_cost / self.quantity
                self.selling_price = round_up_to_nearest_half(self.cost_per_unit * (1 + (self.profit_margin / 100)))
                self.amount = self.total_cost  # Set payment amount to total cost

    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
        self.calculate_selling_price()
    
    def __repr__(self):
        return f"<Payment {self.id}: {self.payment_type} - GHS {self.amount}>"