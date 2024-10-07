
import os
import threading
import time
from datetime import datetime, timedelta
import sqlite3
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from crewai import Agent, Crew, Task
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='.')
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news_entries
                 (id INTEGER PRIMARY KEY,
                  timestamp DATETIME,
                  title TEXT,
                  content TEXT,
                  source TEXT,
                  sentiment TEXT)''')
    conn.commit()
    conn.close()

init_db()

# CrewAI setup
os.environ["ANTHROPIC_API_KEY"] = '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'
llm = ChatAnthropic(model='claude-3-5-sonnet-20240620', temperature=0.2)

class StockNewsAgent:
    def __init__(self):
        self.search_agent = Agent(
            role='News Searcher',
            goal='Find latest stock news',
            backstory='You are an expert at finding the latest stock news.',
            tools=[DuckDuckGoSearchRun()],
            llm=llm
        )
        self.sentiment_agent = Agent(
            role='Sentiment Analyzer',
            goal='Analyze sentiment of news articles',
            backstory='You are skilled at determining the sentiment of financial news.',
            llm=llm
        )
        self.running = False
        self.status = "Idle"
        self.progress = 0
        self.next_run_time = None
        self.company_symbol = None

    def search_news(self, company_symbol):
        self.status = "Searching news"
        self.progress = 33
        task = Task(
            description=f"Find the latest news about {company_symbol} stock",
            expected_output='The news content in markdown format',
            agent=self.search_agent
        )
        crew = Crew(agents=[self.search_agent], tasks=[task])
        result = crew.kickoff()
        return str(result)

    def analyze_sentiment(self, news_content):
        self.status = "Analyzing sentiment"
        self.progress = 66
        task = Task(
            description=f"Analyze the sentiment of this news: {news_content}",
            expected_output='Either the word "positive" or "negative"',
            agent=self.sentiment_agent
        )
        crew = Crew(agents=[self.sentiment_agent], tasks=[task])
        result = crew.kickoff()
        return str(result)

    def store_news_entry(self, news_data):
        self.status = "Storing news entry"
        self.progress = 90
        conn = sqlite3.connect('news.db')
        c = conn.cursor()
        c.execute('''INSERT INTO news_entries (timestamp, title, content, source, sentiment)
                     VALUES (?, ?, ?, ?, ?)''',
                  (datetime.now(), news_data['title'], news_data['content'],
                   news_data['source'], news_data['sentiment']))
        conn.commit()
        conn.close()

    def run(self, company_symbol):
        self.company_symbol = company_symbol
        while self.running:
            try:
                self.status = "Starting cycle"
                self.progress = 0
                news = self.search_news(company_symbol)
                sentiment = self.analyze_sentiment(news)
                self.store_news_entry({
                    'title': f"News about {company_symbol}",
                    'content': news,
                    'source': 'CrewAI Search',
                    'sentiment': sentiment
                })
                self.status = "Cycle completed"
                self.progress = 100
                self.next_run_time = datetime.now() + timedelta(seconds=10)
                time.sleep(10)  # Wait for an hour before next search
            except Exception as e:
                print(f"Error in agent run: {str(e)}")
                self.status = "Error occurred"
                self.next_run_time = datetime.now() + timedelta(minutes=5)
                time.sleep(300)  # Wait for 5 minutes before retrying
            finally:
                self.progress = 0

agent = StockNewsAgent()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/run', methods=['POST'])
def run_agent():
    data = request.json
    company_symbol = data.get('company_symbol')
    if not company_symbol:
        return jsonify({"error": "Company symbol is required"}), 400
    
    if not agent.running:
        agent.running = True
        threading.Thread(target=agent.run, args=(company_symbol,)).start()
        return jsonify({"message": f"Agent started for {company_symbol}"}), 200
    else:
        return jsonify({"message": "Agent is already running"}), 400

@app.route('/stop', methods=['POST'])
def stop_agent():
    if agent.running:
        agent.running = False
        agent.status = "Stopped"
        agent.progress = 0
        agent.next_run_time = None
        return jsonify({"message": "Agent stopped"}), 200
    else:
        return jsonify({"message": "Agent is not running"}), 400

@app.route('/status', methods=['GET'])
def get_agent_status():
    return jsonify({
        "running": agent.running,
        "status": agent.status,
        "progress": agent.progress,
        "next_run_time": agent.next_run_time.isoformat() if agent.next_run_time else None,
        "company_symbol": agent.company_symbol
    })

@app.route('/news', methods=['GET'])
def get_news():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'timestamp')
    order = request.args.get('order', 'desc')

    conn = sqlite3.connect('news.db')
    c = conn.cursor()

    if search:
        query = f'''SELECT * FROM news_entries 
                   WHERE title LIKE ? OR content LIKE ?
                   ORDER BY {sort} {order}
                   LIMIT ? OFFSET ?'''
        search_param = f'%{search}%'
        c.execute(query, (search_param, search_param, per_page, (page - 1) * per_page))
    else:
        query = f'''SELECT * FROM news_entries 
                   ORDER BY {sort} {order}
                   LIMIT ? OFFSET ?'''
        c.execute(query, (per_page, (page - 1) * per_page))

    entries = [dict(zip(['id', 'timestamp', 'title', 'content', 'source', 'sentiment'], row))
               for row in c.fetchall()]
    
    conn.close()

    return jsonify(entries)

@app.route('/news/<int:id>', methods=['GET'])
def get_news_detail(id):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('SELECT * FROM news_entries WHERE id = ?', (id,))
    entry = c.fetchone()
    conn.close()

    if entry:
        return jsonify(dict(zip(['id', 'timestamp', 'title', 'content', 'source', 'sentiment'], entry)))
    else:
        return jsonify({"error": "News entry not found"}), 404

if __name__ == '__main__':
    app.run(host='localhost', port=7594, debug=True)
