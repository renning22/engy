import os
from typing import Dict, List, Optional

import litellm
from dotenv import load_dotenv
from pydantic import BaseModel


def auto_load_dotenv():
    # Get the current working directory
    current_dir = os.getcwd()
    
    # Construct the path to the .env file
    env_path = os.path.join(current_dir, '.env')
    
    # Check if the .env file exists
    if os.path.exists(env_path):
        # Load the .env file
        load_dotenv(env_path)
        print(f"Loaded .env file from {env_path}")
    else:
        load_dotenv()


auto_load_dotenv()


class ChatMessage(BaseModel):
    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

    def to_string(self) -> str:
        return f"{self.role}: {self.content}"


def query_llm(prompt: str, *,
              system_message: str = '',
              previous_history: List[ChatMessage] = [],
              filename: Optional[str] = None,
              model: Optional[str] = None,
              max_tokens: int = 4096,
              temperature: float = 0.1):
    extra_headers = {}
    if not model:
        model = os.getenv('MODEL', 'claude-3-5-sonnet-20240620')
    if '3-5-sonnet' in model:
        max_tokens = 8000
        extra_headers = {"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"}
    n = int(os.getenv('BATCH_INFERENCE_N', '1'))
    if n == 1:
        n = None

    messages: List[ChatMessage] = (
        previous_history + [ChatMessage(role='user', content=prompt)])
    if filename is not None:
        with open(f'{filename}.prompt.txt', 'w') as f:
            f.write(f'{model}\n\n{system_message}\n\n')
            for i, message in enumerate(messages):
                f.write(f'=== {i}: {message.role} ===\n')
                f.write(message.content)
                f.write('\n')

    final_messages = [msg.to_dict() for msg in messages]
    if system_message:
        final_messages = [
            {"role": "system", "content": system_message}] + final_messages

    response = litellm.completion(
        model=model,
        messages=final_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        num_retries=1,
        n=n,
        extra_headers=extra_headers,
    )
    replys = [choice.message.content for choice in response.choices]
    histories = []
    for reply in replys:
        new_messages = messages + \
            [ChatMessage(role='assistant', content=reply)]
        histories.append(new_messages)
    if filename is not None:
        with open(f'{filename}.prompt.txt', 'a') as f:
            for i, reply in enumerate(replys):
                f.write(f'\n=== Reply {i} ===\n')
                f.write(reply)
    return replys, histories
