import os
from crewai import Agent, Task, Crew
from textwrap import dedent

from crewai_tools import DirectoryReadTool, FileReadTool

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


def create_crew(step_callback):
    directory_tool = DirectoryReadTool(directory='./doc')
    file_read_tool = FileReadTool()

    # Create an agent to summarize OKRs
    okr_summarizer = Agent(
        role='OKR Summarizer',
        goal='Provide concise and informative summaries of team OKRs and related information',
        backstory=dedent("""
            You are an expert in analyzing and summarizing Objectives and Key Results (OKRs) and related team information.
            Your task is to review the team's OKRs, member information, and any additional reports to provide clear, 
            concise summaries that highlight the most important aspects of each team member's objectives, key results, 
            and recent activities.
        """),
        tools=[directory_tool, file_read_tool],
        verbose=True
    )

    # Create a task for summarizing OKRs and team information
    summarize_task = Task(
        description=dedent("""
            1. List all files in the './doc' directory.
            2. Read and parse the contents of './doc/team_okrs.json' and './doc/team_members.json'.
            3. Analyze any additional files (e.g., weekly reports) if present.
            4. Provide a summary for each team member, including:
            - Name and role
            - Objectives and key results
            - Recent activities or progress (if available from additional files)
            5. Highlight any common themes or alignments across the team.
            6. If any weekly reports are found, incorporate their insights into the summary.

            Start by listing the files in the './doc' directory.
        """,
        ),
        expected_output='A paragrah describe okr with current progress.',
        agent=okr_summarizer
    )

    # Create the crew with the OKR summarizer agent
    okr_crew = Crew(
        agents=[okr_summarizer],
        tasks=[summarize_task],
        step_callback=step_callback,
        verbose=True
    )
    return okr_crew


def run_agent(step_callback):
    crew = create_crew(step_callback)
    result = crew.kickoff()
    print("###################### Result:")
    print(result)


if __name__ == '__main__':
    def print_callback(step_output):
        print(step_output)
    run_agent(print_callback)