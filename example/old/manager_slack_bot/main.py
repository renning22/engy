# pip install requests slack-sdk slack-bolt
import threading
import time

import requests
# from agent import run_agent
from weekly_report_agent import run_agent
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from langchain_core.agents import AgentFinish


# Use environment variables for tokens
SLACK_BOT_TOKEN = "xoxb-7420780031075-7406839909431-KygOX30Tcjl72gW6uU10y3rg"
SLACK_APP_TOKEN = "xapp-1-A07CD7Z7HBM-7421460837250-5453f3567b1f87127c41b9e9bb40262e686ce0ed118bb2a913ebc78f1ee60dc0"
CHANNEL_ID = "C07BYRPKXPH"


# Initialize the Web API client
web_client = WebClient(token=SLACK_BOT_TOKEN)

# Initialize your app with your bot token and socket mode handler
app = App(token=SLACK_BOT_TOKEN)



def update_home_tab(client, event, logger):
    try:
        # Call views.publish with the user ID and view payload
        client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to admin console, <@" + event["user"] + ">!* :house:"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "App Integration",
                            "emoji": True
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Sign-in Asana",
                                    "emoji": True
                                },
                                "value": "asana",
                                "action_id": "signin_button_click"
                            }
                        ]
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Sign-in Jira",
                                    "emoji": True
                                },
                                "value": "jira",
                                "action_id": "signin_button_click"
                            }
                        ]
                    },
                    {
                        "type": "divider"
                    },
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.event("app_home_opened")
def handle_app_home_opened(client, event, logger):
    print('app_home_opened')
    update_home_tab(client, event, logger)


@app.action("signin_button_click")
def handle_signin_button_click(ack, body, client, logger):
    ack()
    try:
        # Send a message to the user
        client.chat_postMessage(
            channel=body["user"]["id"],
            text="You clicked the signin_button_click in the App Home! :tada:"
        )
    except Exception as e:
        logger.error(f"Error handling button click: {e}")


def send_interactive_message(channel_id):
    app.client.chat_postMessage(
        channel=channel_id,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Welcome! Please select a fruit and enter your name:"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a fruit"
                        },
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Apple"},
                                "value": "apple"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Banana"},
                                "value": "banana"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Cherry"},
                                "value": "cherry"
                            }
                        ],
                        "action_id": "fruit_selection"
                    }
                ]
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "name_input"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Your name"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Submit"
                        },
                        "action_id": "submit_button"
                    }
                ]
            }
        ]
    )


@app.action("fruit_selection")
def handle_fruit_selection(ack, body, logger):
    ack()
    print(f"Fruit selected: {body['actions'][0]['selected_option']['value']}")



@app.action("name_input")
def handle_name_input(ack, body, logger):
    ack()
    print(f"Name entered: {body['actions'][0]['value']}")


@app.action("submit_button")
def handle_submission(ack, body, logger):
    ack()
    # Retrieve the selected fruit and entered name from the state
    import pprint
    pprint.pprint(body)
    # fruit = body['state']['values']['fruit_selection']['selected_option']['value']
    # name = body['state']['values']['name_input']['value']
    # print(f"Thank you, {name}! You selected {fruit}.")


def send_message(channel, message, thread_ts=None):
    try:
        result = web_client.chat_postMessage(
            channel=channel,
            text=message,
            thread_ts=thread_ts
        )
        print(f"Message sent: {result['ts']}")
    except SlackApiError as e:
        if e.response["error"] == "not_in_channel":
            print(
                f"Error: Bot is not in the channel {channel}. Please invite the bot to the channel.")
        elif e.response["error"] == "channel_not_found":
            print(
                f"Error: Channel {channel} not found. Please check the channel ID.")
        else:
            print(f"Error sending message: {e}")


def periodic_message():
    message_count = 0
    while True:
        message_count += 1
        message = f"This is periodic message #{message_count}"
        # send_message(CHANNEL_ID, message)
        time.sleep(5)  # Wait for 5 seconds


@app.command("/interact")
def interact_command(ack, body, respond):
    ack()
    send_interactive_message(body['channel_id'])


@app.command("/checkin")
def checkin_command(ack, body, respond):
    ack()
    channel_id = body['channel_id']
    
    # Extract the text from the command
    command_text = body['text'].strip()
    
    if not command_text:
        respond("Please provide a name with the /checkin command.", response_type="ephemeral")
        return

    # Send the initial message and get the timestamp
    initial_message = web_client.chat_postMessage(
        channel=channel_id,
        text=f"Ok, agent is running, generate weekly report for {command_text}..."
    )
    thread_ts = initial_message['ts']

    def step_callback(output):
        if isinstance(output, AgentFinish):
            try:
                final_output = output.return_values['output']
                send_message(channel_id, final_output, thread_ts)
            except:
                pass
        else:
            assert isinstance(output, list)
            for action, observation in output:
                st = f"""{action.type}(tool='{action.tool}', tool_input='{action.tool_input}', observation={len(observation)})"""
                send_message(channel_id, st, thread_ts)

    result = run_agent(step_callback, command_text)
    send_message(channel_id, result, thread_ts)


@app.event("file_shared")
def handle_file_shared(event, say, client):
    try:
        # Get file information
        file_id = event["file_id"]
        file_info = client.files_info(file=file_id)
        file = file_info["file"]
        if file["mimetype"] == "application/vnd.google-apps.document":
            # This is a Google Doc
            doc_name = file["name"]
            doc_url = file["url_private"]
            
            say(f"A Google Doc named '{doc_name}' has been shared.\n"
                f"You can access it here: {doc_url}\n\n"
                f"If you need me to analyze its content, please copy and paste the relevant parts into our chat.")
        else:
            # General file 
            file_name = file_info["file"]["name"]
            file_url = file_info["file"]["url_private_download"]

            # Download the file
            headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
            response = requests.get(file_url, headers=headers)

            # Save the file locally
            with open(f"downloaded_{file_name}", "wb") as f:
                f.write(response.content)

            # Acknowledge receipt of the file
            say(f"Received and saved file: {file_name}")

            print(f"Successfully downloaded and saved: {file_name}")

    except Exception as e:
        print(f"Error handling file: {e}")



@app.event("message")
def handle_message_events(body, say):
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
