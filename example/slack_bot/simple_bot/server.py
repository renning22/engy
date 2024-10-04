
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from slack import WebClient
from slack.errors import SlackApiError

app = Flask(__name__)
CORS(app)

# Mock Slack configuration (replace with real values in production)
SLACK_BOT_TOKEN = "xoxb-7420780031075-7406839909431-KygOX30Tcjl72gW6uU10y3rg"
SLACK_CHANNEL = "#test_manager_bot"

# Initialize Slack client
slack_client = WebClient(token=SLACK_BOT_TOKEN)

def send_slack_message(message):
    try:
        response = slack_client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=message
        )
        return True, "Message sent successfully"
    except SlackApiError as e:
        return False, f"Error sending message: {str(e)}"

@app.route('/api/send_message', methods=['POST'])
def api_send_message():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400

    success, message = send_slack_message(data['message'])
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='localhost', port=6639)
