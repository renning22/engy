
import os
from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import pandas as pd
import json
from io import StringIO

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

def create_mock_data():
    products = ['Product A', 'Product B', 'Product C', 'Product D']
    start_date = datetime(2023, 1, 1)
    for _ in range(1000):
        sale = Sale(
            product_name=products[_ % len(products)],
            sale_date=start_date + timedelta(days=_ // 10),
            quantity=(_ % 5) + 1,
            price=(_ % 100) + 10
        )
        db.session.add(sale)
    db.session.commit()

def initialize_database():
    db.create_all()
    if Sale.query.count() == 0:
        create_mock_data()

def get_quarter(date):
    return (date.month - 1) // 3 + 1

@app.route('/init', methods=['GET'])
def init():
    initialize_database()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/quarterly_revenue', methods=['GET'])
def quarterly_revenue():
    sales = Sale.query.all()
    df = pd.DataFrame([(sale.sale_date, sale.quantity * sale.price) for sale in sales],
                      columns=['date', 'revenue'])
    df['quarter'] = df['date'].apply(lambda x: f"{x.year}Q{get_quarter(x)}")
    quarterly_revenue = df.groupby('quarter')['revenue'].sum().reset_index()
    return jsonify(quarterly_revenue.to_dict(orient='records'))

@app.route('/api/quarterly_breakdown/<quarter>', methods=['GET'])
def quarterly_breakdown(quarter):
    year, q = quarter.split('Q')
    start_date = datetime(int(year), (int(q) - 1) * 3 + 1, 1)
    end_date = start_date + timedelta(days=90)
    sales = Sale.query.filter(Sale.sale_date >= start_date, Sale.sale_date < end_date).all()
    df = pd.DataFrame([(sale.product_name, sale.quantity * sale.price) for sale in sales],
                      columns=['product', 'revenue'])
    breakdown = df.groupby('product')['revenue'].sum().reset_index()
    return jsonify(breakdown.to_dict(orient='records'))

@app.route('/api/sales_report', methods=['GET', 'POST'])
def sales_report():
    if request.method == 'GET':
        sales = Sale.query.all()
        df = pd.DataFrame([(sale.product_name, sale.sale_date, sale.quantity, sale.price) for sale in sales],
                          columns=['product', 'date', 'quantity', 'price'])
        df['revenue'] = df['quantity'] * df['price']
        report = df.to_html(index=False)
        
        template = """
        <html>
        <head><title>Sales Report</title></head>
        <body>
            <h1>Sales Report</h1>
            {{ report|safe }}
        </body>
        </html>
        """
        return render_template_string(template, report=report)
    
    elif request.method == 'POST':
        data = request.json
        df = pd.read_json(StringIO(json.dumps(data)))
        
        # Update database with new data
        Sale.query.delete()
        for _, row in df.iterrows():
            sale = Sale(
                product_name=row['product'],
                sale_date=pd.to_datetime(row['date']),
                quantity=row['quantity'],
                price=row['price']
            )
            db.session.add(sale)
        db.session.commit()
        
        return jsonify({"message": "Sales report updated successfully"})

if __name__ == '__main__':
    app.run(host='localhost', port=5008, debug=True)
