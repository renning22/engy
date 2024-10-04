import json
import crewai
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.agents import AgentFinish
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)

# Assume ANTHROPIC_API_KEY and other keys have been set in .env file.
load_dotenv()

# Initialize tools
docs_tool = DirectoryReadTool(directory='.')
file_tool = FileReadTool()
duckduck_tool = DuckDuckGoSearchRun()
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


def step_callback(step_output):
    output = step_output
    if isinstance(output, AgentFinish):
        st = f"""{output.type}({list(output.return_values.keys())})"""
        print(st)
    else:
        assert isinstance(output, list)
        for action, observation in output:
            st = f"""{action.type}(tool='{action.tool}', tool_input='{action.tool_input}', observation={len(observation)})"""
            print(st)


class Agent:
    def __init__(self, name, role, goal, backstory, tools, task_description, expected_output, send_to, receive_from):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools
        self.task_description = task_description
        self.expected_output = expected_output
        self.send_to = send_to
        self.receive_from = receive_from
        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307", temperature=0.2)  # type: ignore

        self.agent = crewai.Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=[search_tool, scrape_tool],
            llm=self.llm
        )

    def execute(self):
        crew = crewai.Crew(
            agents=[self.agent],
            tasks=[
                crewai.Task(
                    description=self.task_description,
                    expected_output=self.expected_output,
                    agent=self.agent
                )
            ],
            step_callback=step_callback
        )
        result = str(crew.kickoff())
        return result


def construct_py_file_from_json(json_file, output_file='agents.py'):
    print('Generate "agents.py"')
    # Open the file
    with open(json_file, 'r') as f:
        # Load the JSON data
        data = json.load(f)

    py_content = '''from finae import Agent

# finae.Agent is my agent implementation.
# The overview of finae.Agent class. 
# 
# class Agent:
#   def __init__(self, name, role, goal, backstory, tools, task_description, expected_output, send_to, receive_from):
#     self.name = name
#     self.role = role
#     self.goal = goal
#     self.backstory = backstory
#     self.tools = tools
#     self.task_description = task_description
#     self.expected_output = expected_output
#     self.send_to = send_to
#     self.receive_from = receive_from
#     ...
#
#   def execute(self) -> str:
#     """Execute and return expected_output in string."""

all_agents = []
'''
    for agent_def in data:
        agent_py = f'''

all_agents.append(Agent(
    name="{agent_def['name']}",
    role="{agent_def['role']}",
    goal="{agent_def['goal']}",
    backstory="{agent_def['backstory']}",
    tools={str(agent_def['tools'])},
    task_description="{agent_def['task_description']}",
    expected_output="{agent_def['expected_output']}",
    send_to={str(agent_def['send_to'])},
    receive_from={str(agent_def['receive_from'])},
))
'''
        py_content += agent_py

    with open(output_file, 'w') as f:
        f.write(py_content)


if __name__ == '__main__':
    agent = Agent(
        name="Sophia Patel",
        role="Content Synthesizer",
        goal="Synthesize information and craft compelling narratives",
        backstory="Skilled content writer and editor with a background in business journalism. Sophia has a talent for distilling complex information into clear, engaging prose.",
        tools=["search_tool", "scrape_tool", "duckduck_tool"],
        task_description="Task Goal: Create a comprehensive report synthesizing all gathered information. Steps: 1) Review data from Market Data Analyst and Target Audience and Competitor Analyst. 2) Write an executive summary highlighting key findings. 3) Develop detailed sections on market overview, target audience, and competitive landscape. 4) Formulate strategic recommendations based on the analysis. 5) Format the report in Markdown for easy readability.",
        expected_output="Markdown-formatted report with sections: 'Executive Summary', 'Market Overview', 'Target Audience', 'Competitive Landscape', and 'Strategic Recommendations'",
        send_to=["Ethan Novak"],
        receive_from=["Olivia Thompson", "Marcus Chen"]
    )
    agent.execute()
