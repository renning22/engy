
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from sympy import symbols, diff, integrate, sympify, SympifyError

app = Flask(__name__)
CORS(app)

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b

def derivative(expr, var='x'):
    x = symbols(var)
    try:
        expr = sympify(expr)
        result = diff(expr, x)
        return str(result)
    except SympifyError:
        raise ValueError("Invalid expression")

def integral(expr, var='x'):
    x = symbols(var)
    try:
        expr = sympify(expr)
        result = integrate(expr, x)
        return str(result)
    except SympifyError:
        raise ValueError("Invalid expression")

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    if not data or 'operation' not in data:
        return jsonify({"error": "Invalid input"}), 400

    operation = data['operation']

    try:
        if operation in ['add', 'subtract', 'multiply', 'divide']:
            if 'a' not in data or 'b' not in data:
                return jsonify({"error": "Missing operands"}), 400
            a = float(data['a'])
            b = float(data['b'])
            if operation == 'add':
                result = add(a, b)
            elif operation == 'subtract':
                result = subtract(a, b)
            elif operation == 'multiply':
                result = multiply(a, b)
            elif operation == 'divide':
                result = divide(a, b)
        elif operation in ['derivative', 'integral']:
            if 'expression' not in data:
                return jsonify({"error": "Missing expression"}), 400
            expression = data['expression']
            if operation == 'derivative':
                result = derivative(expression)
            elif operation == 'integral':
                result = integral(expression)
        else:
            return jsonify({"error": "Invalid operation"}), 400

        return jsonify({"result": str(result)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7036)
