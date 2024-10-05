
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database models
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    is_recurring = db.Column(db.Boolean, default=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Helper functions
def expense_to_dict(expense):
    return {
        'id': expense.id,
        'date': expense.date.isoformat(),
        'amount': expense.amount,
        'description': expense.description,
        'category_id': expense.category_id,
        'is_recurring': expense.is_recurring
    }

def category_to_dict(category):
    return {
        'id': category.id,
        'name': category.name
    }

# Serve index.html
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# API routes
@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    return jsonify([expense_to_dict(expense) for expense in expenses])

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    new_expense = Expense(
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        amount=data['amount'],
        description=data['description'],
        category_id=data['category_id'],
        is_recurring=data['is_recurring']
    )
    db.session.add(new_expense)
    db.session.commit()
    return jsonify(expense_to_dict(new_expense)), 201

@app.route('/expenses/<int:id>', methods=['PUT'])
def update_expense(id):
    expense = Expense.query.get_or_404(id)
    data = request.json
    expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    expense.amount = data['amount']
    expense.description = data['description']
    expense.category_id = data['category_id']
    expense.is_recurring = data['is_recurring']
    db.session.commit()
    return jsonify(expense_to_dict(expense))

@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return '', 204

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([category_to_dict(category) for category in categories])

@app.route('/categories', methods=['POST'])
def add_category():
    data = request.json
    new_category = Category(name=data['name'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify(category_to_dict(new_category)), 201

@app.route('/expenses/summary', methods=['GET'])
def get_expense_summary():
    total_by_category = db.session.query(
        Category.name,
        func.sum(Expense.amount).label('total')
    ).join(Expense).group_by(Category.name).all()

    recurring_expenses = db.session.query(func.sum(Expense.amount)).filter(Expense.is_recurring == True).scalar() or 0
    one_time_expenses = db.session.query(func.sum(Expense.amount)).filter(Expense.is_recurring == False).scalar() or 0

    return jsonify({
        'total_by_category': dict(total_by_category),
        'recurring_expenses': recurring_expenses,
        'one_time_expenses': one_time_expenses
    })

if __name__ == '__main__':
    app.run(host='localhost', port=7896, debug=True)
