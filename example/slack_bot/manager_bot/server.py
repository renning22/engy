
import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging

app = Flask(__name__, static_folder='.')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Slack API configuration
SLACK_BOT_TOKEN = "xoxb-7420780031075-7406839909431-KygOX30Tcjl72gW6uU10y3rg"
slack_client = WebClient(token=SLACK_BOT_TOKEN)

# SQLite database configuration
DB_NAME = "team_management.db"

# Document upload configuration
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS team_members
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  slack_id TEXT NOT NULL,
                  last_check_in TEXT,
                  current_report TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS schedules
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  interval_days INTEGER,
                  day_of_week TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS integrations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  service TEXT NOT NULL,
                  access_token TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

def send_slack_message(channel, message):
    try:
        response = slack_client.chat_postMessage(channel=channel, text=message)
        return response
    except SlackApiError as e:
        logger.error(f"Error sending message: {e}")
        return None

def process_slack_response(user_id, response_text):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE team_members SET last_check_in = ?, current_report = ? WHERE slack_id = ?",
              (datetime.now().isoformat(), response_text, user_id))
    conn.commit()
    conn.close()

def send_check_in_messages():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT slack_id FROM team_members")
    members = c.fetchall()
    conn.close()

    for member in members:
        send_slack_message(member[0], "It's time for your check-in. How's your progress?")

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        return jsonify({"message": "File uploaded successfully"}), 200

@app.route('/add_member', methods=['POST'])
def add_member():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO team_members (name, slack_id) VALUES (?, ?)",
              (data['name'], data['slack_id']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Member added successfully"}), 201

@app.route('/get_members', methods=['GET'])
def get_members():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM team_members")
    members = [{"id": row[0], "name": row[1], "slack_id": row[2], "last_check_in": row[3], "current_report": row[4]}
               for row in c.fetchall()]
    conn.close()
    return jsonify(members), 200

@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM schedules")
    c.execute("INSERT INTO schedules (interval_days, day_of_week) VALUES (?, ?)",
              (data['interval_days'], data['day_of_week']))
    conn.commit()
    conn.close()

    # Update the scheduler
    scheduler.remove_all_jobs()
    scheduler.add_job(send_check_in_messages, 'cron', day_of_week=data['day_of_week'])

    return jsonify({"message": "Schedule updated successfully"}), 200

@app.route('/get_schedule', methods=['GET'])
def get_schedule():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM schedules")
    schedule = c.fetchone()
    conn.close()
    if schedule:
        return jsonify({"interval_days": schedule[1], "day_of_week": schedule[2]}), 200
    else:
        return jsonify({"message": "No schedule found"}), 404

def generate_calendar_data(year, month):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT interval_days, day_of_week FROM schedules")
    schedule = c.fetchone()
    conn.close()

    if not schedule:
        return []

    interval_days, day_of_week = schedule
    start_date = datetime(year, month, 1)
    end_date = start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1)

    calendar_data = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.strftime("%A").lower() == day_of_week.lower():
            calendar_data.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    return calendar_data

@app.route('/get_calendar', methods=['GET'])
def get_calendar():
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    calendar_data = generate_calendar_data(year, month)
    return jsonify(calendar_data), 200

@app.route('/signin/asana')
def signin_asana():
    # TODO: Implement Asana OAuth flow
    # This is a placeholder. You need to implement the actual OAuth flow here.
    return redirect("https://app.asana.com/-/oauth_authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code")

@app.route('/signin/slack')
def signin_slack():
    # TODO: Implement Slack OAuth flow
    # This is a placeholder. You need to implement the actual OAuth flow here.
    return redirect("https://slack.com/oauth/v2/authorize?client_id=YOUR_CLIENT_ID&scope=chat:write,channels:read&redirect_uri=YOUR_REDIRECT_URI")

@app.route('/oauth/asana/callback')
def asana_callback():
    # TODO: Handle Asana OAuth callback
    # This is a placeholder. You need to implement the token exchange and storage here.
    code = request.args.get('code')
    # Exchange code for token
    # Store token in database
    return jsonify({"message": "Asana integration successful"}), 200

@app.route('/oauth/slack/callback')
def slack_callback():
    # TODO: Handle Slack OAuth callback
    # This is a placeholder. You need to implement the token exchange and storage here.
    code = request.args.get('code')
    # Exchange code for token
    # Store token in database
    return jsonify({"message": "Slack integration successful"}), 200

@app.route('/send_test_messages', methods=['POST'])
def send_test_messages():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT slack_id FROM team_members")
    members = c.fetchall()
    conn.close()

    success_count = 0
    for member in members:
        try:
            response = send_slack_message(member[0], "This is a test message from Kim, your Slack Bot Manager Assistant!")
            if response and response['ok']:
                success_count += 1
        except Exception as e:
            logger.error(f"Error sending test message to {member[0]}: {str(e)}")

    return jsonify({
        "message": f"Test messages sent successfully to {success_count} out of {len(members)} members",
        "success_count": success_count,
        "total_members": len(members)
    }), 200

@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"An error occurred: {str(e)}")
    return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5030, debug=True)
