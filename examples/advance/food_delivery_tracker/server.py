
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func

app = Flask(__name__, static_folder='.')
CORS(app)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'delivery_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

# Database models
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivery_events = db.relationship('DeliveryEvent', backref='order', lazy=True)

class DeliveryEvent(db.Model):
    __tablename__ = 'delivery_events'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    region = db.Column(db.String(50))

class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200))

class Region(db.Model):
    __tablename__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Helper function for logging
def log_request(request, response):
    app.logger.info(f"Request: {request.method} {request.url}")
    app.logger.info(f"Request data: {request.json}")
    app.logger.info(f"Response: {response.status_code}")
    app.logger.info(f"Response data: {response.json}")

# Serve index.html
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# API endpoints
@app.route('/api/orders', methods=['GET'])
def get_orders():
    customer_id = request.args.get('customer_id')
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Order.query

    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    if status:
        query = query.filter(Order.status == status)
    if start_date:
        query = query.filter(Order.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Order.created_at <= datetime.fromisoformat(end_date))

    orders = query.all()
    result = [{'id': o.id, 'customer_id': o.customer_id, 'status': o.status, 'created_at': o.created_at.isoformat()} for o in orders]
    
    response = jsonify(result)
    log_request(request, response)
    return response

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    order = Order.query.get_or_404(order_id)
    events = [{'id': e.id, 'event_type': e.event_type, 'timestamp': e.timestamp.isoformat(), 'driver_id': e.driver_id, 'region': e.region} for e in order.delivery_events]
    
    result = {
        'id': order.id,
        'customer_id': order.customer_id,
        'status': order.status,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
        'delivery_events': events
    }
    
    response = jsonify(result)
    log_request(request, response)
    return response

@app.route('/api/delivery_events', methods=['GET', 'POST'])
def handle_delivery_events():
    if request.method == 'GET':
        order_id = request.args.get('order_id')
        driver_id = request.args.get('driver_id')
        region = request.args.get('region')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = DeliveryEvent.query

        if order_id:
            query = query.filter(DeliveryEvent.order_id == order_id)
        if driver_id:
            query = query.filter(DeliveryEvent.driver_id == driver_id)
        if region:
            query = query.filter(DeliveryEvent.region == region)
        if start_date:
            query = query.filter(DeliveryEvent.timestamp >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(DeliveryEvent.timestamp <= datetime.fromisoformat(end_date))

        events = query.all()
        result = [{'id': e.id, 'order_id': e.order_id, 'event_type': e.event_type, 'timestamp': e.timestamp.isoformat(), 'driver_id': e.driver_id, 'region': e.region} for e in events]
        
        response = jsonify(result)
        log_request(request, response)
        return response

    elif request.method == 'POST':
        data = request.json
        new_event = DeliveryEvent(
            order_id=data['order_id'],
            event_type=data['event_type'],
            driver_id=data.get('driver_id'),
            region=data.get('region')
        )
        db.session.add(new_event)
        db.session.commit()

        result = {'id': new_event.id, 'message': 'Delivery event created successfully'}
        response = jsonify(result), 201
        log_request(request, response)
        return response

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.json
    order.status = data['status']
    order.updated_at = datetime.utcnow()
    db.session.commit()

    result = {'id': order.id, 'message': 'Order status updated successfully'}
    response = jsonify(result)
    log_request(request, response)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6151, debug=True)
