from typing import Callable
from crewai_tools import ScrapeWebsiteTool

scrape_tool = ScrapeWebsiteTool()


def web_scraper_agent(url: str, producer: Callable[[dict], None]):
    content = scrape_tool.run(website_url=url)
    producer({'url': url, 'webpage_content': content})


def _terminal_producer(entity):
    print(f"Produced entity: {entity}")


if __name__ == '__main__':
    web_scraper_agent('https://engy.ai', _terminal_producer)
