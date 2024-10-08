import random
import time
from typing import Callable

from ..llm import query_llm

SYSTEM_PROMPT = '''**Role:** You are a creative review generation agent for Airbnb.
**Goal:** Create realistic and diverse customer reviews based on common Airbnb experiences, using the provided customer name and review platform.
**Process:**
1. Generate a variety of review content, considering different aspects of Airbnb stays.
2. Vary the tone, length, and focus of reviews to simulate real customer feedback.
3. Incorporate the provided customer name and platform naturally into the review when appropriate.
4. Output the generated review content in <REVIEW_CONTENT></REVIEW_CONTENT> blocks.
'''


def parse_review_content(text):
    """
    Parses a string containing `<REVIEW_CONTENT>` blocks and returns them as a list.
    """
    reviews = []
    start_index = 0
    while True:
        open_tag = text.find("<REVIEW_CONTENT>", start_index)
        if open_tag == -1:
            break
        close_tag = text.find("</REVIEW_CONTENT>", open_tag)
        if close_tag == -1:
            raise ValueError("Missing closing tag for REVIEW_CONTENT")
        review = text[open_tag + len("<REVIEW_CONTENT>"): close_tag]
        reviews.append(review.strip())
        start_index = close_tag + len("</REVIEW_CONTENT>")
    return reviews


def generate_name():
    first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William",
                   "Mia", "James", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Henry", "Evelyn", "Alexander"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_platform():
    platforms = ["Airbnb.com", "Google Reviews", "TripAdvisor",
                 "Booking.com", "VRBO", "Facebook", "Yelp", "Android", "App Store"]
    return random.choice(platforms)


def airbnb_review_agent(producer: Callable[[dict], None], num_reviews: int = 1):
    for _ in range(num_reviews):
        name = generate_name()
        platform = generate_platform()

        query = f"""Generate a realistic Airbnb customer review for the following:
Customer Name: {name}
Review Platform: {platform}
Ensure the review is detailed, mentioning specific aspects of the Airbnb experience, and naturally incorporate the customer's name and platform when appropriate."""
        responses, _ = query_llm(query, system_message=SYSTEM_PROMPT,
                                 model="claude-3-haiku-20240307", temperature=0.7, filename='airbnb_review_agent')
        review_contents = parse_review_content(responses[0])
        if review_contents:
            review = {
                "name": name,
                "date": time.strftime("%Y-%m-%d"),
                "platform": platform,
                "review_content": review_contents[0]
            }
            producer(review)


def _terminal_producer(review):
    print(f"Generated review: {review}")


if __name__ == '__main__':
    airbnb_review_agent(_terminal_producer)
