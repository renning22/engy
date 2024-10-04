import os
import time
import threading
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Use environment variables for tokens
SLACK_BOT_TOKEN = "xoxb-7420780031075-7406839909431-KygOX30Tcjl72gW6uU10y3rg"
SLACK_APP_TOKEN = "xapp-1-A07CD7Z7HBM-7421460837250-5453f3567b1f87127c41b9e9bb40262e686ce0ed118bb2a913ebc78f1ee60dc0"
CHANNEL_ID = "C07BYRPKXPH"

# Initialize the Web API client
web_client = WebClient(token=SLACK_BOT_TOKEN)

# Initialize your app with your bot token and socket mode handler
app = App(token=SLACK_BOT_TOKEN)

def send_message(channel, message):
    try:
        result = web_client.chat_postMessage(
            channel=channel,
            text=message
        )
        print(f"Message sent: {result['ts']}")
    except SlackApiError as e:
        if e.response["error"] == "not_in_channel":
            print(f"Error: Bot is not in the channel {channel}. Please invite the bot to the channel.")
        elif e.response["error"] == "channel_not_found":
            print(f"Error: Channel {channel} not found. Please check the channel ID.")
        else:
            print(f"Error sending message: {e}")

def periodic_message():
    message_count = 0
    while True:
        message_count += 1
        message = f"This is periodic message #{message_count}"
        # send_message(CHANNEL_ID, message)
        time.sleep(5)  # Wait for 5 seconds

@app.event("message")
def handle_message_events(body, logger):
    print(f"Received body: {body}")

    event = body["event"]
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if user_id and text:
        print(f"Received message: {text}")
        
        # Simple response logic
        if 'hello' in text.lower():
            response = f"Hello <@{user_id}>! How can I help you?"
        elif 'bye' in text.lower():
            response = f"Goodbye <@{user_id}>! Have a great day!"
        else:
            response = f"You said: {text}"
        
        send_message(channel_id, response)

def main():
    # Start the periodic message thread
    periodic_thread = threading.Thread(target=periodic_message)
    periodic_thread.daemon = True
    periodic_thread.start()

    # Start your app
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    main()