
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import difflib
import os

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/compare', methods=['POST'])
def compare_texts():
    data = request.json
    text1 = data.get('text1', '')
    text2 = data.get('text2', '')
    
    diff_html = generate_diff(text1, text2)
    return jsonify({'diff': diff_html})

def generate_diff(text1, text2):
    differ = difflib.HtmlDiff(wrapcolumn=70)
    diff = differ.make_file(text1.splitlines(), text2.splitlines())
    
    # Customize the diff output
    custom_diff = diff.replace(
        '<table class="diff" id="difflib_chg_to0__top"',
        '<table class="diff" id="difflib_chg_to0__top" style="width:100%; border-collapse: collapse;"'
    )
    custom_diff = custom_diff.replace(
        '<td class="diff_header"',
        '<td class="diff_header" style="padding: 5px; text-align: right; width: 40px; background-color: #f0f0f0;"'
    )
    custom_diff = custom_diff.replace(
        '<td nowrap="nowrap"',
        '<td nowrap="nowrap" style="padding: 5px; white-space: pre-wrap; font-family: monospace;"'
    )
    
    return custom_diff

if __name__ == '__main__':
    app.run(host='localhost', port=9079, debug=True)
