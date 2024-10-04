
import os
import tempfile
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
import markdown

app = Flask(__name__, static_folder='.')
CORS(app)

# In-memory storage for the latest summary
latest_summary = {}

# Load environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

# Initialize ChatAnthropic
chat_model = ChatAnthropic(model="claude-3-5-sonnet-20240620", anthropic_api_key=ANTHROPIC_API_KEY)

# Create CrewAI agent
summarizer_agent = Agent(
    role='Document Summarizer',
    goal='Provide concise and accurate summaries of documents',
    backstory='You are an expert in summarizing complex documents quickly and accurately.',
    allow_delegation=False,
    llm=chat_model
)

def summarize_document(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    summarize_task = Task(
        description=f"Summarize the following document:\n\n{content}\n\nProvide a concise summary that captures the main points and key information.",
        expected_output="Output in markdown format",
        agent=summarizer_agent
    )

    crew = Crew(
        agents=[summarizer_agent],
        tasks=[summarize_task],
        verbose=True
    )

    result = str(crew.kickoff())

    print('333333\n', result)
    return result

def convert_to_markdown(text):
    # For this example, we'll assume the text is already in a format close to markdown
    # You may need to add more sophisticated conversion logic depending on your needs
    return markdown.markdown(text)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            print('1111111 ', temp_file.name)
            file.save(temp_file.name)
            try:
                summary = summarize_document(temp_file.name)
                markdown_summary = convert_to_markdown(summary)
                session_id = request.form.get('session_id', 'default')
                latest_summary[session_id] = markdown_summary
                return jsonify({"message": "File processed successfully"}), 200
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({"error": str(e)}), 500
            finally:
                os.unlink(temp_file.name)

@app.route('/summary', methods=['GET'])
def get_summary():
    session_id = request.args.get('session_id', 'default')
    summary = latest_summary.get(session_id)
    if summary:
        return jsonify({"summary": summary}), 200
    else:
        return jsonify({"error": "No summary available for this session"}), 404

@app.route('/download', methods=['GET'])
def download_summary():
    session_id = request.args.get('session_id', 'default')
    summary = latest_summary.get(session_id)
    if summary:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as temp_file:
            temp_file.write(summary)
            temp_file_path = temp_file.name
        return send_file(temp_file_path, as_attachment=True, download_name='summary.md')
    else:
        return jsonify({"error": "No summary available for this session"}), 404

if __name__ == '__main__':
    app.run(host='localhost', port=8409, debug=True)
