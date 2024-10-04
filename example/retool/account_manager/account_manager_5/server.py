
import os
import logging
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE

app = Flask(__name__, static_folder='.')
CORS(app)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'transactions.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    deposit_complete_amount = db.Column(db.Float, nullable=False)
    withdraw_complete_amount = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)
    deposit_other_amount = db.Column(db.Float, nullable=False)
    withdraw_amount = db.Column(db.Float, nullable=False)
    withdraw_other_amount = db.Column(db.Float, nullable=False)

class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    week = fields.Int(required=True, validate=validate.Range(min=1, max=52))
    deposit_complete_amount = fields.Float(required=True, validate=validate.Range(min=0))
    withdraw_complete_amount = fields.Float(required=True, validate=validate.Range(min=0))
    deposit_amount = fields.Float(required=True, validate=validate.Range(min=0))
    deposit_other_amount = fields.Float(required=True, validate=validate.Range(min=0))
    withdraw_amount = fields.Float(required=True, validate=validate.Range(min=0))
    withdraw_other_amount = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        unknown = EXCLUDE

transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    username = request.args.get('username', None)

    query = Transaction.query

    if username:
        query = query.filter(Transaction.username.ilike(f'%{username}%'))

    transactions = query.paginate(page=page, per_page=per_page, error_out=False)
    result = transactions_schema.dump(transactions.items)

    logger.info(f"Retrieved {len(result)} transactions (page {page}, per_page {per_page}, username filter: {username})")
    return jsonify({
        'transactions': result,
        'total': transactions.total,
        'pages': transactions.pages,
        'current_page': page
    })

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = transaction_schema.load(request.json)
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify(err.messages), 400

    new_transaction = Transaction(**data)
    db.session.add(new_transaction)
    db.session.commit()

    logger.info(f"Added new transaction with ID: {new_transaction.id}")
    return jsonify(transaction_schema.dump(new_transaction)), 201

@app.route('/api/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    transaction = Transaction.query.get_or_404(id)

    try:
        data = transaction_schema.load(request.json, partial=True)
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify(err.messages), 400

    for key, value in data.items():
        setattr(transaction, key, value)

    db.session.commit()

    logger.info(f"Updated transaction with ID: {id}")
    return jsonify(transaction_schema.dump(transaction))

@app.route('/api/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()

    logger.info(f"Deleted transaction with ID: {id}")
    return '', 204

@app.route('/api/transactions/generate', methods=['POST'])
def generate_random_transaction():
    random_transaction = Transaction(
        username=f"user_{random.randint(1, 1000)}",
        week=random.randint(1, 52),
        deposit_complete_amount=round(random.uniform(0, 10000), 2),
        withdraw_complete_amount=round(random.uniform(0, 10000), 2),
        deposit_amount=round(random.uniform(0, 10000), 2),
        deposit_other_amount=round(random.uniform(0, 10000), 2),
        withdraw_amount=round(random.uniform(0, 10000), 2),
        withdraw_other_amount=round(random.uniform(0, 10000), 2)
    )

    db.session.add(random_transaction)
    db.session.commit()

    logger.info(f"Generated random transaction with ID: {random_transaction.id}")
    return jsonify(transaction_schema.dump(random_transaction)), 201

@app.route('/api/transactions/increase-deposit', methods=['POST'])
def increase_deposit_amount():
    try:
        transactions = Transaction.query.all()
        for transaction in transactions:
            transaction.deposit_amount += 100
        db.session.commit()
        logger.info(f"Increased deposit amount for all transactions by $100")
        return jsonify({"message": "Deposit amount increased by $100 for all transactions"}), 200
    except Exception as e:
        logger.error(f"Error increasing deposit amount: {str(e)}")
        return jsonify({"error": "Failed to increase deposit amount"}), 500

@app.route('/api/transactions/select-withdraw-gt-deposit', methods=['GET'])
def select_withdraw_gt_deposit():
    try:
        transactions = Transaction.query.filter(Transaction.withdraw_complete_amount > Transaction.deposit_complete_amount).all()
        result = transactions_schema.dump(transactions)
        logger.info(f"Selected {len(result)} transactions where Withdraw > Deposit")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error selecting transactions where Withdraw > Deposit: {str(e)}")
        return jsonify({"error": "Failed to select transactions"}), 500

@app.errorhandler(404)
def not_found(error):
    logger.error(f"Not found: {error}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=9273, debug=True)
