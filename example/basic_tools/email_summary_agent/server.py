
import os
import pickle
from flask import Flask, request, redirect, jsonify, send_from_directory
from flask_cors import CORS
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration
CLIENT_ID = '169602758570-or32hkfhmo3vk2s8rnp5q40jto1b72ls.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:8487/callback'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
API_KEY = 'sk-proj-NJsgku9NzwZOBBWOHzJgT3BlbkFJaSzUkcix2y5Ex91L5IAw'

# In-memory storage for tokens and results
tokens = {}
summarized_results = {}

# Gmail API setup
flow = Flow.from_client_config(
    {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    },
    scopes=SCOPES
)

def get_gmail_service(credentials):
    return build('gmail', 'v1', credentials=credentials)

# CrewAI setup
llm = OpenAI(api_key=API_KEY)

summarizer_agent = Agent(
    role='Email Summarizer',
    goal='Provide concise and accurate summaries of emails',
    backstory='You are an AI specialized in quickly understanding and summarizing email content.',
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Routes
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/auth')
def auth():
    authorization_url, _ = flow.authorization_url(prompt='consent')
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    tokens['gmail'] = credentials_to_dict(credentials)
    return 'Authentication successful. You can close this window.'

@app.route('/summarize')
def summarize():
    if 'gmail' not in tokens:
        return jsonify({'error': 'Not authenticated'}), 401

    credentials = get_credentials()
    if not credentials or not credentials.valid:
        return jsonify({'error': 'Invalid credentials'}), 401

    service = get_gmail_service(credentials)
    messages = fetch_recent_emails(service)
    
    summarized_results.clear()
    for msg in messages:
        email_id = msg['id']
        email_content = get_email_content(service, email_id)
        summary = summarize_email(email_content)
        summarized_results[email_id] = summary

    return jsonify({'message': 'Summarization complete', 'count': len(summarized_results)})

@app.route('/results')
def results():
    return jsonify(summarized_results)

# Helper functions
def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_credentials():
    if 'gmail' not in tokens:
        return None
    creds = pickle.loads(pickle.dumps(tokens['gmail']))  # Deep copy
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            tokens['gmail'] = credentials_to_dict(creds)
    return creds

def fetch_recent_emails(service, max_results=50):
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    return results.get('messages', [])

def get_email_content(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message['payload']
    headers = payload.get('headers', [])
    subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
    
    if 'parts' in payload:
        parts = payload['parts']
        data = parts[0]['body']['data']
    else:
        data = payload['body']['data']
    
    # Decode the email content (you might need to handle different encodings)
    # For simplicity, we're assuming it's base64 encoded
    import base64
    text = base64.urlsafe_b64decode(data).decode('utf-8')
    
    return f"Subject: {subject}\n\n{text}"

def summarize_email(email_content):
    task = Task(
        description=f"Summarize the following email:\n\n{email_content}\n\nProvide a concise summary capturing the main points.",
        agent=summarizer_agent
    )
    crew = Crew(
        agents=[summarizer_agent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    return result

if __name__ == '__main__':
    app.run(host='localhost', port=8487, debug=True)
