from datetime import datetime
from extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Added unique constraint
    quantity = db.Column(db.Integer, default=0)
    cost_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    profit_margin = db.Column(db.Float)
    min_stock_level = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Renamed from created_at
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    price = db.Column(db.Float)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    sales = db.relationship('Sale', backref='product', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='product', lazy=True)
    costs = db.relationship('ProductCost', backref='product', lazy=True)

    def update_inventory(self, quantity_change):
        """Update product quantity and return new stock level"""
        self.quantity += quantity_change
        return self.quantity

    def calculate_selling_price(self, margin=None):
        """Calculate selling price based on cost and margin"""
        if margin is not None:
            self.profit_margin = margin
        self.selling_price = round(self.cost_price * (1 + (self.profit_margin / 100)), 2)
        return self.selling_price
    
    class ProductCost(db.Model):
        __tablename__ = 'product_costs'
    
        id = db.Column(db.Integer, primary_key=True)
        product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
        cost_type = db.Column(db.String(50), nullable=False)  # e.g., 'purchase', 'transport', 'storage'
        amount = db.Column(db.Float, nullable=False)
        description = db.Column(db.String(200))
        date = db.Column(db.DateTime, default=datetime.utcnow)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)