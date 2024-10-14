
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from calculator_operations import perform_calculation

app = Flask(__name__)
CORS(app)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    if not data or 'operation' not in data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        result = perform_calculation(data)
        return jsonify({"result": str(result)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9034)
