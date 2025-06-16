from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g, flash
import os
from datetime import datetime
from sqlalchemy import event, Engine
from sqlalchemy.orm import joinedload
from flask_login import current_user, login_required, login_user
from extensions import db, login_manager
from models import User, Product, Sale, Payment
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///akontabu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.template_filter('currency')
def currency_format(value):
    return f"₵{float(value):,.2f}"

# Enable SQLite foreign key constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def round_up_to_half(v): 
    return math.ceil(v * 2) / 2

# Auth middleware
@app.before_request
def load_user():
    if 'user_id' in session:
        # g.user = User.query.get(session['user_id'])
        g.user = db.session.get(User, session['user_id'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # assuming you're using SQLAlchemy and User has an id


# Custom Jinja filter for Ghana Cedis formatting
# @app.template_filter('ghs')
# def format_ghs(value):
#     if value is None:
#         return "GHS 0.00"
#     try:
#         return "GHS {:,.2f}".format(float(value))
#     except (ValueError, TypeError):
#         return "GHS 0.00"

@app.template_filter('currency')
def currency_format(value):
    return f"₵{float(value):,.2f}"

@app.context_processor
def inject_user():
    return dict(current_user=current_user)


# Routes
@app.route('/')
def index(): 
     return render_template ('index.html')

# Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    user = User(
        name=data['name'],
        email=data['email'],
        business_name=data.get('business_name', ''),  # Make sure this is included
            
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        data = request.get_json()
        user = db.session.execute(
    db.select(User).where(User.email == data['email'])
).scalar_one_or_none()
        
        if user and user.check_password(data['password']):
            login_user(user)  # Make sure this is called
            session['user_id'] = user.id
            return jsonify({'message': 'Login successful'}), 200
        
        return jsonify({'message': 'Invalid email or password'}), 401
    except Exception as e:
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    # Calculate totals
    total_sales = db.session.query(db.func.sum(Sale.quantity * Sale.price))\
        .filter(Sale.user_id == current_user.id).scalar() or 0
    
    inventory = Product.query.all()
    
    return render_template('dashboard.html',
                         total_sales=total_sales,
                         inventory=inventory)

# @app.route('/inventory')
# @login_required
# def inventory():
#     products = Product.query.filter_by(user_id=current_user.id).all()
#     return render_template('inventory.html', products=products)

@app.route('/inventory')
@login_required
def inventory():
    products = db.session.query(Product).options(joinedload(Product.payments)).all()

    # Add selling price from the most recent payment (or whatever logic fits)
    for product in products:
     if product.price is None:
        product.price = 0

    for product in products:
        if product.payments:
            latest_payment = sorted(product.payments, key=lambda p: p.date, reverse=True)[0]
            product.selling_price = latest_payment.selling_price
        else:
            product.selling_price = 0

    return render_template('inventory.html', products=products)



'''@app.route('/inventory/new', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()
    try:
        product = Product(
            name=data['name'],
            quantity=data['quantity'],
            cost_price=data['cost_price'],
            selling_price=data['selling_price'],
            profit_margin=((float(data['selling_price']) - float(data['cost_price'])) / float(data['cost_price'])) * 100,
            min_stock_level=data.get('min_stock', 10),
            user_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500 -->'''

# @app.route('/inventory/new', methods=['POST'])
# @login_required
# def add_product():
#     data = request.get_json()
#     try:
#         product = Product(
#             name=data['name'],
#             quantity=data['quantity'],
#             cost_price=data.get('cost_price', 0),
#             selling_price=data.get('price', 0),
#             user_id=current_user.id
#         )
#         db.session.add(product)
#         db.session.commit()
#         return jsonify({
#             'message': 'Product added successfully',
#             'product': {
#                 'id': product.id,
#                 'name': product.name,
#                 'quantity': product.quantity,
#                 'price': product.selling_price
#             }
#         }), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'message': str(e)}), 500


@app.route('/inventory/new', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No JSON data received'}), 400

    try:
        name = data.get('name')
        quantity = data.get('quantity')
        price = data.get('price')
        cost_price = data.get('cost_price', 0)

        # Basic validation
        if not name or quantity is None or price is None:
            return jsonify({'message': 'Missing required fields'}), 400

        # Convert to correct types
        try:
            quantity = int(quantity)
            price = float(price)
            cost_price = float(cost_price)
        except ValueError:
            return jsonify({'message': 'Invalid number for quantity or price'}), 400

        product = Product(
            name=name,
            quantity=quantity,
            cost_price=cost_price,
            selling_price=price,
            user_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()

        return jsonify({
            'message': 'Product added successfully',
            'product': {
                'id': product.id,
                'name': product.name,
                'quantity': product.quantity,
                'price': product.selling_price
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Internal Server Error: {str(e)}'}), 500


@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.get_json()
        product = Product.query.filter_by(id=data['product_id'], user_id=session['user_id']).first()

        if not product:
            return jsonify({'message': 'Product not found'}), 404

        try:
            quantity = int(data['quantity'])
            price = float(data['price'])
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid quantity or price'}), 400

        if quantity > product.quantity:
            return jsonify({'message': 'Not enough stock available'}), 400

        # Reduce inventory
        product.quantity -= quantity

        # Create new sale
        sale = Sale(
            product_id=product.id,
            quantity=quantity,
            price=price,
            user_id=session['user_id'],
            customer=data.get('customer', ''),
            description=data.get('description', '')
        )

        db.session.add(sale)
        db.session.commit()
        return jsonify({'message': 'Sale recorded successfully'}), 201

    # For GET request - load sales and products
    start = request.args.get('start')
    end = request.args.get('end')

    sales_query = Sale.query.filter_by(user_id=session['user_id'])

    if start and end:
        try:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            sales_query = sales_query.filter(Sale.date.between(start_date, end_date))
        except ValueError:
            flash("Invalid date range", "error")

    sales = sales_query.order_by(Sale.date.desc()).all()
    products = Product.query.filter_by(user_id=session['user_id']).all()

    return render_template('sales.html', sales=sales, products=products)


# Placeholder routes for other pages
@app.route('/payments')
@login_required  # Use this instead of manual session checking
def payments():
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.date.desc()).all()
    return render_template('payments.html', payments=payments)

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/inventory/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
        
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
            
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/record-sale', methods=['POST'])
def record_sale():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')
    
    # Validate inputs
    if not product_id or not quantity:
        return jsonify({"error": "Missing data"}), 400
    
    # Save to database (example using SQLAlchemy)
    sale = Sale(product_id=product_id, quantity=quantity)
    db.session.add(sale)
    db.session.commit()
    
    return jsonify({"success": True})

@app.route('/api/products/<int:product_id>/costs')
@login_required
def get_product_costs(product_id):
    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first_or_404()
    costs = [{
        'id': c.id,
        'type': c.cost_type,
        'amount': c.amount,
        'description': c.description,
        'date': c.date.strftime('%Y-%m-%d')
    } for c in product.costs]
    
    return jsonify({
        'product': product.name,
        'total_cost': sum(c.amount for c in product.costs),
        'average_cost': product.cost_price,
        'selling_price': product.selling_price,
        'costs': costs
    })

@app.route('/api/update_product_price', methods=['POST'])
@login_required
def update_product_price():
    data = request.get_json()
    product = Product.query.filter_by(id=data['product_id'], user_id=current_user.id).first_or_404()
    
    # Update product details
    product.cost_price = data['cost_price']
    product.price = data['selling_price']
    product.quantity += int(data['quantity'])
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/payments', methods=['POST'])
@login_required
def record_payment():
    data = request.get_json()
    
    try:
        product = None
        
        if data['payment_type'] == 'product':
            # Validate all required product fields
            required_fields = [
                'product_name', 'quantity', 'base_cost',
                'transportation', 'carriage', 'profit_margin', 'calculated_price'
            ]
            if not all(key in data for key in required_fields):
                return jsonify({'message': 'Missing required product fields'}), 400

            # Convert and validate numeric fields
            try:
                quantity = float(data['quantity'])
                base_cost = float(data['base_cost'])
                transportation = float(data['transportation'])
                carriage = float(data['carriage'])
                profit_margin = float(data['profit_margin'])
            except (ValueError, TypeError):
                return jsonify({'message': 'Invalid numeric values'}), 400

            if quantity <= 0 or base_cost <= 0:
                return jsonify({'message': 'Quantity and cost must be positive'}), 400

            # Calculate total cost and unit price
            total_cost = base_cost + transportation + carriage
            cost_per_unit = total_cost / quantity
            selling_price = round_up_to_half(cost_per_unit * (1 + (profit_margin / 100)))

            # Find or create product
            product = Product.query.filter_by(
                name=data['product_name'],
                user_id=current_user.id
            ).first()

            if not product:
                product = Product(
                    name=data['product_name'],
                    quantity=quantity,
                    cost_price=cost_per_unit,
                    selling_price=selling_price,
                    user_id=current_user.id
                )
                db.session.add(product)
            else:
                # Update existing product using weighted average
                total_quantity = product.quantity + quantity
                product.cost_price = (
                    (product.cost_price * product.quantity) + 
                    cost_per_unit * quantity
                ) / total_quantity
                product.quantity = total_quantity
                product.selling_price = product.cost_price * (1 + (profit_margin / 100))

        # Create payment record
        payment = Payment(
            payment_type=data['payment_type'],
            amount=data.get('amount', total_cost if data['payment_type'] == 'product' else float(data['amount'])),
            description=data.get('description', ''),
            user_id=current_user.id,
            date=datetime.utcnow()
        )

        # Add product-specific fields if this is a product payment
        if data['payment_type'] == 'product':
            payment.product_id = product.id
            payment.product_name = data['product_name']
            payment.quantity = quantity
            payment.base_cost = base_cost
            payment.transportation = transportation
            payment.carriage = carriage
            payment.total_cost = total_cost
            payment.cost_per_unit = cost_per_unit
            payment.profit_margin = profit_margin
            payment.selling_price = selling_price

        db.session.add(payment)
        db.session.commit()

        # Prepare response
        response_data = {
            'date': payment.date.strftime('%Y-%m-%d'),
            'payment_type': payment.payment_type,
            'description': payment.description,
            'amount': payment.amount,
            'selling_price': selling_price if data['payment_type'] == 'product' else None
        }
        
        if product:
            response_data.update({
                'product_id': product.id,
                'product_name': product.name,
                'quantity': product.quantity,
                'unit_cost': cost_per_unit,
                'selling_price': selling_price
            })

        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/payments/<int:payment_id>', methods=['DELETE'])
@login_required
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if payment.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    try:
        db.session.delete(payment)
        db.session.commit()
        return jsonify({'message': 'Deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500
    
@app.route('/api/payments/restore', methods=['POST'])
@login_required
def restore_payment():
    data = request.get_json()
    
    try:
        payment = Payment(
            payment_type=data['payment_type'],
            amount=data['amount'],
            description=data.get('description', ''),
            user_id=current_user.id,
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            product_name=data.get('product_name'),
            quantity=data.get('quantity'),
            base_cost=data.get('base_cost'),
            transportation=data.get('transportation'),
            carriage=data.get('carriage'),
            total_cost=data.get('total_cost'),
            cost_per_unit=data.get('cost_per_unit'),
            profit_margin=data.get('profit_margin'),
            selling_price=data.get('selling_price'),
            product_id=data.get('product_id')
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({
            'message': 'Payment restored',
            'payment_id': payment.id,
            'date': payment.date.strftime('%Y-%m-%d')
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error restoring payment: {str(e)}'}), 500
    
@app.route('/api/payments/<int:id>', methods=['PUT'])
@login_required
def update_payment(id):
    payment = Payment.query.get_or_404(id)

    if payment.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()

    # Update common fields
    payment.payment_type = data['payment_type']
    payment.amount = data.get('amount')
    payment.description = data.get('description')

    # If it's a product payment, update product details
    if data['payment_type'] == 'product':
        quantity = data.get('quantity', 1)
        base_cost = data.get('base_cost', 0)
        transportation = data.get('transportation', 0)
        carriage = data.get('carriage', 0)
        total_cost = base_cost + transportation + carriage
        cost_per_unit = total_cost / quantity if quantity else 0
        selling_price = data.get('calculated_price', 0)
        amount = round(quantity * selling_price, 2)

        payment.product_name = data['product_name']
        payment.quantity = quantity
        payment.base_cost = base_cost
        payment.transportation = transportation
        payment.carriage = carriage
        payment.total_cost = total_cost
        payment.cost_per_unit = cost_per_unit
        payment.profit_margin = data.get('profit_margin', 0)
        payment.selling_price = selling_price
        payment.amount = amount


    db.session.commit()

    return jsonify({'message': 'Payment updated successfully'})

@app.route('/api/payments/<int:id>', methods=['GET'])
@login_required
def get_payment(id):
    payment = Payment.query.get_or_404(id)
    
    if payment.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    return jsonify({
        'id': payment.id,
        'payment_type': payment.payment_type,
        'description': payment.description,
        'amount': payment.amount,
        'product_name': payment.product_name,
        'quantity': payment.quantity,
        'base_cost': payment.base_cost,
        'transportation': payment.transportation,
        'carriage': payment.carriage,
        'total_cost': payment.total_cost,
        'cost_per_unit': payment.cost_per_unit,
        'profit_margin': payment.profit_margin,
        'selling_price': payment.selling_price,
        'date': payment.date.strftime('%Y-%m-%d'),
        'product_id': payment.product_id
    })




 # Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)