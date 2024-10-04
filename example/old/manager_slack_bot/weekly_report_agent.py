import os
from crewai import Agent, Task, Crew
from textwrap import dedent

from crewai_tools import DirectoryReadTool, FileReadTool
from langchain_anthropic import ChatAnthropic

# serper.dev API key
os.environ["SERPER_API_KEY"] = "754f0c3ef821cc19c52dba5d4b1e8fbd923090e0"
os.environ["ANTHROPIC_API_KEY"] = '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'

model = 'claude-3-5-sonnet-20240620'

LLM = ChatAnthropic(model=model, temperature=0.9)


def create_crew(step_callback, member_name):
    directory_tool = DirectoryReadTool()
    file_read_tool = FileReadTool()

    file_lister = Agent(
        role='File Lister',
        goal='List all files in the current directory',
        backstory="You are responsible for listing all files in the current directory.",
        tools=[directory_tool],
        verbose=True,
        llm=LLM,
    )

    okr_reader = Agent(
        role='OKR Reader',
        goal='Read and parse the team OKRs file',
        backstory="You are responsible for reading and parsing the team OKRs file.",
        tools=[file_read_tool],
        verbose=True,
        llm=LLM,
    )

    member_reader = Agent(
        role='Member Reader',
        goal='Read and parse the team members file',
        backstory="You are responsible for reading and parsing the team members file.",
        tools=[file_read_tool],
        verbose=True,
        llm=LLM,
    )

    weekly_data_reader = Agent(
        role='Weekly Data Reader',
        goal=f"Read and parse {member_name}'s weekly data file if it exists",
        backstory=f"You are responsible for reading and parsing {member_name}'s weekly data file if it exists.",
        tools=[file_read_tool],
        verbose=True,
        llm=LLM,
    )

    report_generator = Agent(
        role='Weekly Report Generator',
        goal=f'Generate a comprehensive weekly report for {member_name}',
        backstory=dedent(f"""
            You are an expert in analyzing team data and generating detailed weekly reports.
            Your task is to review the team's OKRs, member information, and any additional data
            to create a comprehensive weekly report for {member_name}.
            You provide clear, concise outputs for each task.
        """),
        verbose=True,
        llm=LLM,
    )

    # Task 1: List files in directory
    list_files_task = Task(
        description="List all files in the current directory.",
        expected_output="A list of file names in the current directory.",
        agent=file_lister
    )

    # Task 2: Read team OKRs
    read_okrs_task = Task(
        description="Read and parse the contents of 'team_okrs.json'.",
        expected_output="The parsed contents of the team OKRs file.",
        agent=okr_reader,
        context=[list_files_task]
    )

    # Task 3: Read team members
    read_members_task = Task(
        description="Read and parse the contents of 'team_members.json'.",
        expected_output="The parsed contents of the team members file.",
        agent=member_reader,
        context=[list_files_task]
    )

    # Task 4: Read weekly data (if available)
    read_weekly_data_task = Task(
        description=f"If a file named '{member_name}_weekly_data.json' exists, read and parse its contents. If not, state that no weekly data file was found.",
        expected_output=f"The parsed contents of {member_name}'s weekly data file, or a message stating no file was found.",
        agent=weekly_data_reader,
        context=[list_files_task]
    )

    # Task 5: Generate report
    generate_report_task = Task(
        description=dedent(f"""
            Using the information gathered from previous tasks, generate a weekly report for {member_name}, including:
            - Name and role (from team members data)
            - Objectives and key results (from team OKRs data)
            - Progress on each KR (from weekly data if available)
            - Notable achievements or challenges faced this week
            - Plans or focus areas for the upcoming week
            Format the report in a clear, professional manner.
        """),
        expected_output=f"A comprehensive weekly report for {member_name}.",
        agent=report_generator,
        context=[list_files_task, read_okrs_task,
                 read_members_task, read_weekly_data_task]
    )

    # Create the crew with all agents and chained tasks
    report_crew = Crew(
        agents=[file_lister, okr_reader, member_reader,
                weekly_data_reader, report_generator],
        tasks=[
            list_files_task,
            read_okrs_task,
            read_members_task,
            read_weekly_data_task,
            generate_report_task
        ],
        step_callback=step_callback,
        verbose=True
    )
    return report_crew


def run_agent(step_callback, member_name):
    crew = create_crew(step_callback, member_name)
    result = crew.kickoff()
    print(f"###################### Weekly Report for {member_name}:")
    print(result)
    return str(result)


if __name__ == '__main__':
    def print_callback(step_output):
        print(step_output)

    member_name = input(
        "Enter the name of the team member for the weekly report: ")
    run_agent(print_callback, member_name)
