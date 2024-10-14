
from basic_operations import add, subtract, multiply, divide
from advanced_operations import derivative, integral, solve_equation, expand_expression, factor_expression

def perform_calculation(data):
    operation = data['operation']

    if operation in ['add', 'subtract', 'multiply', 'divide']:
        if 'a' not in data or 'b' not in data:
            raise ValueError("Missing operands")
        a = float(data['a'])
        b = float(data['b'])
        if operation == 'add':
            return add(a, b)
        elif operation == 'subtract':
            return subtract(a, b)
        elif operation == 'multiply':
            return multiply(a, b)
        elif operation == 'divide':
            return divide(a, b)
    elif operation in ['derivative', 'integral', 'solve', 'expand', 'factor']:
        if 'expression' not in data:
            raise ValueError("Missing expression")
        expression = data['expression']
        if operation == 'derivative':
            return derivative(expression)
        elif operation == 'integral':
            return integral(expression)
        elif operation == 'solve':
            return solve_equation(expression)
        elif operation == 'expand':
            return expand_expression(expression)
        elif operation == 'factor':
            return factor_expression(expression)
    else:
        raise ValueError("Invalid operation")
