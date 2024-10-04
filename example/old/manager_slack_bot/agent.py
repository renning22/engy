import io
import os
import pickle
import datetime

import dash_bootstrap_components as dbc
import pandas as pd
from crewai import Agent, Crew, Task
from langchain_core.agents import AgentFinish
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from langchain_anthropic import ChatAnthropic

# serper.dev API key
os.environ["SERPER_API_KEY"] = "754f0c3ef821cc19c52dba5d4b1e8fbd923090e0"

# You can choose to use a local model through Ollama for example. See https://docs.crewai.com/how-to/LLM-Connections/ for more information.

# os.environ["OPENAI_MODEL_NAME"] ='gpt-4o'  # Adjust based on available model
# os.environ["OPENAI_API_KEY"] ='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'

os.environ["OPENAI_API_BASE"] = 'https://shale.live/v1'
# Adjust based on available model
os.environ["OPENAI_MODEL_NAME"] = 'microsoft/Phi-3-mini-128k-instruct'
os.environ["OPENAI_API_KEY"] = 'trapile.ai'

os.environ["ANTHROPIC_API_KEY"] = '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'

# model = 'claude-3-haiku-20240307'
model = 'claude-3-5-sonnet-20240620'

# You can pass an optional llm attribute specifying what model you wanna use.
# It can be a local model through Ollama / LM Studio or a remote
# model like OpenAI, Mistral, Antrophic or others (https://docs.crewai.com/how-to/LLM-Connections/)
#
# import os
# os.environ['OPENAI_MODEL_NAME'] = 'gpt-3.5-turbo'
#
# OR
#
# from langchain_openai import ChatOpenAI

search_icp = 'US based companies, ~20-200 employees, Seed - Series B'
seed_search_query = 'Find 10 such companies, ideally in the software/tech space.'

step_outputs_timestamp = datetime.datetime.now()
step_outputs = []

# if os.path.exists('step_outputs.pickle'):
#     with open('step_outputs.pickle', 'rb') as f:
#         step_outputs = pickle.load(f)


# def step_callback(step_output):
#     step_outputs.append(step_output)
#     with open('step_outputs.pickle', 'wb') as f:
#         pickle.dump(step_outputs, f)

#     global step_outputs_timestamp
#     step_outputs_timestamp = datetime.datetime.now()


def create_crew(input_search_icp, input_seed_search_query, step_callback):
    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()

    contact_finder = Agent(
        role='Comanpy Seacher',
        goal='Search qualified company based on given comapny ICP (Idea Customer Profile)',
        backstory="""You are an expert in company searching industry. You are good at just by searching through public internet like scraping company official site, related news articles to find out relevant contacts.""",
        verbose=True,
        allow_delegation=False,
        # You can pass an optional llm attribute specifying what model you wanna use.
        llm=ChatAnthropic(model=model, temperature=0.9),
        tools=[search_tool, scrape_tool]
    )

    task1 = Task(
        description=f"""1. Search ICP: {input_search_icp}
2. Seed search query: {input_seed_search_query}

Based on "search ICP", use "seed search query" in search tool to list some qualified companies in CSV format.
You may try different variation queries to populate a diverse list.

You can infer "country", "employee_numbers" and "fundraise_round" from the search results.
""",
        expected_output="""Return in CSV format with exact header [company_full_name, official_website, country, employee_numbers, fundraise_round]

The output must follow:
```csv
company_full_name, official_website, country, employee_numbers, fundraise_round
...
...
```
    """,
        agent=contact_finder
    )

    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[contact_finder],
        tasks=[task1],
        step_callback=step_callback,
        verbose=2,  # You can set it to 1 or 2 to different logging levels
        output_log_file='1.log',
    )
    return crew


def run_agent(step_callback):
    crew = create_crew(search_icp, seed_search_query, step_callback)
    result = crew.kickoff()
    print("###################### Result:")
    print(result)
