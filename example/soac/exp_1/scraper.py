"""
Write a python function to parse above texts into entities.
Assume there is a "produce()" function, for every entity, call "produce(entity)" once to output it.

The function signature should be

```python
def parse_entities(input_text, produce):
  ...
```
"""
import types

import engy

from crewai_tools import (
    SerperDevTool,
    ScrapeWebsiteTool
)

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


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


def produce(entity):
    print(f"Produced entity: {entity}")


def main():
    results = search_tool.run(query='engy.ai')
    parse_entities_function(results, produce)


if __name__ == '__main__':
    main()
