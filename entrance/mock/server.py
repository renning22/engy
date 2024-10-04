import os
import subprocess
import threading
import time

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__, static_folder='.')
CORS(app)
socketio = SocketIO(app)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


def get_next_folder_number():
    existing_folders = [f for f in os.listdir() if f.isdigit()
                        and os.path.isdir(f)]
    if not existing_folders:
        return 0
    return max(map(int, existing_folders)) + 1


def run_command(idea):
    try:
        folder_number = get_next_folder_number()
        folder_name = str(folder_number)
        os.makedirs(folder_name, exist_ok=True)
        os.chdir(folder_name)

        with open('input.txt', 'w') as f:
            f.write(idea)

        command = "conda run --no-capture-output -n engy engy --log-to-file"

        process = subprocess.Popen(command, shell=True)

        socketio.emit('output', {'output': f"Generating app #{folder_name}\n"})

        # Wait for the file to be created (with timeout)
        log_file_path = 'terminal.log'
        timeout = 10  # 10 seconds timeout
        start_time = time.time()
        while not os.path.exists(log_file_path):
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Timeout waiting for {log_file_path} to be created")
            time.sleep(0.1)

        with open(log_file_path, 'r') as log_file:
            while process.poll() is None:  # While the process is still running
                line = log_file.readline()
                if line:
                    socketio.emit('output', {'output': line.strip()})
                    socketio.sleep(0)
                else:
                    time.sleep(0.1)  # Short sleep to prevent busy waiting

            # Read any remaining lines after the process has finished
            for line in log_file:
                socketio.emit('output', {'output': line.strip()})
                socketio.sleep(0)

        socketio.emit('output', {
                      'output': f"\nApp #{folder_name} has been generated! (return code {process.returncode})"})
        socketio.emit(
            'output', {'output': f"\nPlease ask admin for App #{folder_name}"})

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        socketio.emit('output', {'output': error_message})

    finally:
        os.chdir('..')
        socketio.emit('generation_complete')


@socketio.on('generate')
def handle_generate(data):
    idea = data['idea']
    threading.Thread(target=run_command, args=(idea,)).start()


if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0', port='8050')
