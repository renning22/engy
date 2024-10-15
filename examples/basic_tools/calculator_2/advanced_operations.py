
from sympy import symbols, diff, integrate, sympify, SympifyError, solve, expand, factor

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

def solve_equation(expr):
    x = symbols('x')
    try:
        expr = sympify(expr)
        result = solve(expr, x)
        return str(result)
    except SympifyError:
        raise ValueError("Invalid expression")

def expand_expression(expr):
    try:
        expr = sympify(expr)
        result = expand(expr)
        return str(result)
    except SympifyError:
        raise ValueError("Invalid expression")

def factor_expression(expr):
    try:
        expr = sympify(expr)
        result = factor(expr)
        return str(result)
    except SympifyError:
        raise ValueError("Invalid expression")
