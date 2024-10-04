import asyncio
import json
import random
import websockets

# Database of Three Kingdoms characters
characters = [
    {"name": "Liu Bei", "kingdom": "Shu", "title": "Emperor of Shu Han"},
    {"name": "Guan Yu", "kingdom": "Shu", "title": "God of War"},
    {"name": "Zhang Fei", "kingdom": "Shu", "title": "General Who Subdues Rebels"},
    {"name": "Zhuge Liang", "kingdom": "Shu", "title": "Prime Minister of Shu"},
    {"name": "Cao Cao", "kingdom": "Wei", "title": "Emperor of Wei"},
    {"name": "Xiahou Dun", "kingdom": "Wei", "title": "One-eyed Warrior"},
    {"name": "Sima Yi", "kingdom": "Wei", "title": "Strategist of Wei"},
    {"name": "Sun Quan", "kingdom": "Wu", "title": "Emperor of Wu"},
    {"name": "Zhou Yu", "kingdom": "Wu", "title": "Talented Strategist"},
    {"name": "Lu Su", "kingdom": "Wu", "title": "Advisor of Wu"}
]

async def send_character_info(websocket):
    while True:
        # Randomly select a character
        character = random.choice(characters)
        
        # Convert character info to JSON
        message = json.dumps(character)
        
        # Send the character info to the client
        await websocket.send(message)
        
        # Wait for 1 second before sending the next character
        await asyncio.sleep(1)

async def handle_client(websocket, path):
    print(f"New client connected: {websocket.remote_address}")
    try:
        await send_character_info(websocket)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())