import asyncio
import websockets
import json

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Three Kingdoms Characters</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f0f0;
        }
        h1 {
            text-align: center;
            color: #4a4a4a;
        }
        #character-info {
            background-color: white;
            border: 1px solid #ddd;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        #kingdom-filter {
            margin-bottom: 20px;
        }
        #character-list {
            list-style-type: none;
            padding: 0;
        }
        #character-list li {
            background-color: white;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        .kingdom-shu { border-left: 5px solid #4CAF50; }
        .kingdom-wei { border-left: 5px solid #2196F3; }
        .kingdom-wu { border-left: 5px solid #F44336; }
    </style>
</head>
<body>
    <h1>Three Kingdoms Characters</h1>
    <div id="kingdom-filter">
        <label for="kingdom-select">Filter by Kingdom:</label>
        <select id="kingdom-select">
            <option value="all">All Kingdoms</option>
            <option value="Shu">Shu</option>
            <option value="Wei">Wei</option>
            <option value="Wu">Wu</option>
        </select>
    </div>
    <div id="character-info">
        <h2>Current Character</h2>
        <p><strong>Name:</strong> <span id="char-name"></span></p>
        <p><strong>Kingdom:</strong> <span id="char-kingdom"></span></p>
        <p><strong>Title:</strong> <span id="char-title"></span></p>
    </div>
    <h2>Character History</h2>
    <ul id="character-list"></ul>

    <script>
        const socket = new WebSocket('ws://localhost:8765');
        const characterInfo = document.getElementById('character-info');
        const charName = document.getElementById('char-name');
        const charKingdom = document.getElementById('char-kingdom');
        const charTitle = document.getElementById('char-title');
        const characterList = document.getElementById('character-list');
        const kingdomSelect = document.getElementById('kingdom-select');

        socket.onmessage = function(event) {
            const character = JSON.parse(event.data);
            
            // Update current character info
            charName.textContent = character.name;
            charKingdom.textContent = character.kingdom;
            charTitle.textContent = character.title;

            // Add character to the list
            const listItem = document.createElement('li');
            listItem.classList.add(`kingdom-${character.kingdom.toLowerCase()}`);
            listItem.innerHTML = `<strong>${character.name}</strong> (${character.kingdom}) - ${character.title}`;
            characterList.prepend(listItem);

            // Limit the list to the last 10 characters
            if (characterList.children.length > 10) {
                characterList.removeChild(characterList.lastChild);
            }

            // Apply kingdom filter
            applyKingdomFilter();
        };

        kingdomSelect.addEventListener('change', applyKingdomFilter);

        function applyKingdomFilter() {
            const selectedKingdom = kingdomSelect.value;
            const listItems = characterList.getElementsByTagName('li');

            for (let item of listItems) {
                if (selectedKingdom === 'all' || item.textContent.includes(`(${selectedKingdom})`)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            }
        }

        socket.onopen = function(event) {
            console.log('Connected to WebSocket server');
        };

        socket.onerror = function(error) {
            console.error('WebSocket Error:', error);
        };

        socket.onclose = function(event) {
            console.log('Disconnected from WebSocket server');
        };
    </script>
</body>
</html>
'''

def generate_random_id(length=8):
    """Generate a random target ID."""
    return 'codeSnippetContainer'

def create_message():
    """Create a message with random JavaScript code and target ID."""
    javascript_code = f"document.getElementById('{generate_random_id()}').innerHTML = 'Hello, WebSocket!';"
    target_id = generate_random_id()
    
    message = {
        "type": "code_snippet",
        "code": javascript_code,
        "targetId": target_id
    }
    
    return json.dumps(message)

def create_html_message(count):
    message = {
        "type": "html",
        "code": HTML[:count],
    }
    return json.dumps(message)


count = 0

async def websocket_server(websocket, path):
    """Handle WebSocket connections and send messages."""
    global count
    count = 0
    try:
        while True:
            message = create_html_message(count)
            await websocket.send(message)
            if count > len(HTML):
                return
            count = count + 1000
            # print(f"Sent: {message}")
            await asyncio.sleep(1)  # Wait for 5 seconds before sending the next message
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    server = await websockets.serve(websocket_server, "localhost", 5678)
    print("WebSocket server started at ws://localhost:5678/")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())