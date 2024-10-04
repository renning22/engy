"""
Write a python function to parse above texts into entities.
Assume there is a "produce()" function, for every entity, call "produce(entity)" once to output it.

The function signature should be

```python
def parse_entities(input_text, produce):
  ...
```
"""
import random
import types
from typing import Callable

from crewai_tools import ScrapeWebsiteTool, SerperDevTool

from ..llm import query_llm

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


SYSTEM_PROMPT = '''**Role:** You are a versatile search query generation agent.

**Goal:** Create relevant search queries based on the provided <PROBLEM></PROBLEM>.

**Process:**
1. Analyze the <PROBLEM> to extract keywords and concepts.
2. Brainstorm search queries using various search techniques.
3. Output the generated search queries in <SEARCH_QUERY></SEARCH_QUERY> block.
'''


def get_parsed_function(code_string):
    # Create a new namespace
    namespace = {}

    # Execute the code in the new namespace
    exec(code_string, namespace)

    # Get the function object from the namespace
    parse_function = namespace.get('parse_entities')

    # Check if the function was successfully defined
    if not isinstance(parse_function, types.FunctionType):
        raise ValueError(
            "Failed to extract 'parse_entities' function from the code")

    return parse_function


code_string = '''
import re

def parse_entities(input_text, produce):
    # Split the input text into individual snippets
    snippets = input_text.split('---')
    
    for snippet in snippets:
        # Extract title, link, and content
        title_match = re.search(r'Title: (.+)', snippet)
        link_match = re.search(r'Link: (.+)', snippet)
        snippet_match = re.search(r'Snippet: (.+)', snippet, re.DOTALL)
        
        if title_match and link_match and snippet_match:
            title = title_match.group(1).strip()
            link = link_match.group(1).strip()
            content = snippet_match.group(1).strip()
            
            # Create an entity dictionary
            entity = {
                'title': title,
                'link': link,
                'content': content
            }
            
            # Call the produce function for each entity
            produce(entity)
        elif link_match and snippet_match:
            # Handle the case where there's no title (first snippet)
            link = link_match.group(1).strip()
            content = snippet_match.group(1).strip()
            
            # Create an entity dictionary
            entity = {
                'link': link,
                'content': content
            }
            
            # Call the produce function for each entity
            produce(entity)
'''

# Get the function object
parse_entities_function = get_parsed_function(code_string)


def parse_search_queries(text):
    """
    Parses a string containing `<SEARCH_QUERY>` blocks and returns them as a list.

    Args:
        text: The input string containing the search queries.

    Returns:
        A list of strings, each representing a single search query.
    """
    queries = []
    start_index = 0
    while True:
        open_tag = text.find("<SEARCH_QUERY>", start_index)
        if open_tag == -1:
            break
        close_tag = text.find("</SEARCH_QUERY>", open_tag)
        if close_tag == -1:
            raise ValueError("Missing closing tag for SEARCH_QUERY")
        query = text[open_tag + len("<SEARCH_QUERY>"): close_tag]
        queries.append(query.strip())  # Remove leading/trailing whitespace
        start_index = close_tag + len("</SEARCH_QUERY>")
    return queries


def web_search_agent(problem: str, producer: Callable[[dict], None]):
    query = f'''<PROBLEM>
{problem}
</PROBLEM>

Brainstorm a random search query.
'''
    responses, _ = query_llm(query, system_message=SYSTEM_PROMPT,
                             model="claude-3-haiku-20240307", temperature=1, filename='web_search_agent')
    search_queries = parse_search_queries(responses[0])
    if search_queries:
        random_query = random.choice(search_queries)
        results = search_tool.run(query=random_query)
        parse_entities_function(results, producer)


def _terminal_producer(entity):
    print(f"Produced entity: {entity}")


if __name__ == '__main__':
    web_search_agent('engy.ai', _terminal_producer)
