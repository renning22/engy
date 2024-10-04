
import os
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.agents import AgentFinish

# Set up the language model
model = 'claude-3-haiku-20240307'
os.environ["ANTHROPIC_API_KEY"] = 'xxxx'
llm = ChatAnthropic(model=model, temperature=0.2)

# Initialize tools
search_tool = DuckDuckGoSearchRun()

# Create agents
dr_amelia_reeves = Agent(
    role='Research Director',
    goal='Define research scope and methodology',
    backstory='Experienced research director with a Ph.D. in Information Science. Amelia excels at designing comprehensive research plans and ensuring projects stay on track.',
    tools=[search_tool],
    llm=llm
)

lucas_ortiz = Agent(
    role='Data Scientist',
    goal='Gather and analyze primary data',
    backstory='Skilled data scientist with expertise in both quantitative and qualitative research methods. Lucas has a talent for uncovering insights from complex datasets and conducting in-depth interviews.',
    tools=[search_tool],
    llm=llm
)

zara_chen = Agent(
    role='Research Analyst',
    goal='Conduct literature review and secondary research',
    backstory='Librarian turned research analyst with a knack for finding and synthesizing information from diverse sources. Zara is adept at using various databases and academic resources.',
    tools=[search_tool],
    llm=llm
)

oliver_nkosi = Agent(
    role='Insights Specialist',
    goal='Interpret findings and develop key insights',
    backstory='Former management consultant with a background in strategy. Oliver specializes in connecting dots between different pieces of information and identifying actionable insights.',
    tools=[search_tool],
    llm=llm
)

sophia_larsson = Agent(
    role='Technical Writer',
    goal='Write and structure the report',
    backstory='Experienced technical writer with a background in journalism. Sophia excels at organizing complex information into clear, logical structures and writing engaging, accessible prose.',
    tools=[search_tool],
    llm=llm
)

dr_rajesh_patel = Agent(
    role='Scientific Reviewer',
    goal='Ensure scientific rigor and accuracy',
    backstory='Academic researcher and peer reviewer with expertise in multiple fields. Rajesh has a keen eye for methodological issues and ensures all claims are properly supported by evidence.',
    tools=[search_tool],
    llm=llm
)

emma_dubois = Agent(
    role='Data Visualization Specialist',
    goal='Create data visualizations and design report layout',
    backstory='Graphic designer specializing in data visualization and report design. Emma has a talent for presenting complex information in visually appealing and easily digestible formats.',
    tools=[search_tool],
    llm=llm
)

# Step callback function
def step_callback(step_output, callback_fn):
    if isinstance(step_output, AgentFinish):
        status = "completed"
        result = step_output.return_values.get('output', '')
    else:
        status = "in_progress"
        result = str(step_output)
    
    callback_fn({
        'status': status,
        'result': result
    })

# Create tasks
def create_tasks(callback_fn):
    return [
        Task(
            description="Define research scope, objectives, and methodology",
            agent=dr_amelia_reeves,
            expected_output="Detailed research plan including research questions, methodology, and timeline",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Conduct literature review and gather secondary research",
            agent=zara_chen,
            expected_output="Comprehensive literature review document with key findings and sources",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Design and conduct primary research (surveys, interviews, etc.)",
            agent=lucas_ortiz,
            expected_output="Raw data from primary research activities in structured format (e.g., CSV, JSON)",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Analyze primary data and extract key insights",
            agent=lucas_ortiz,
            expected_output="Analysis report with statistical findings and qualitative insights",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Synthesize findings from primary and secondary research",
            agent=oliver_nkosi,
            expected_output="Comprehensive synthesis document highlighting main findings and their implications",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Create data visualizations for key findings",
            agent=emma_dubois,
            expected_output="Set of charts, graphs, and infographics illustrating main research results",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Develop report outline and structure",
            agent=sophia_larsson,
            expected_output="Detailed report outline with sections and subsections",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Write first draft of the report",
            agent=sophia_larsson,
            expected_output="First draft of the full research report in markdown format",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Review report for scientific rigor and accuracy",
            agent=dr_rajesh_patel,
            expected_output="Reviewed document with suggestions for improvements and corrections",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Incorporate feedback and refine report",
            agent=sophia_larsson,
            expected_output="Revised draft of the research report",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Design final report layout and integrate visualizations",
            agent=emma_dubois,
            expected_output="Formatted report with integrated graphics and consistent design",
            callback=lambda output: step_callback(output, callback_fn)
        ),
        Task(
            description="Conduct final review and proofreading",
            agent=dr_amelia_reeves,
            expected_output="Final, polished research report ready for submission",
            callback=lambda output: step_callback(output, callback_fn)
        )
    ]

# Function to run the research and report writing process
def research_and_write_report(topic, callback_fn):
    print(f"Starting research and report writing process on the topic: {topic}")
    
    tasks = create_tasks(callback_fn)
    
    crew = Crew(
        agents=[dr_amelia_reeves, lucas_ortiz, zara_chen, oliver_nkosi, sophia_larsson, dr_rajesh_patel, emma_dubois],
        tasks=tasks,
        process=Process.sequential
    )
    
    result = crew.kickoff()
    print("Research and report writing process completed.")
    return result

# Example usage
if __name__ == "__main__":
    def print_callback(data):
        print(f"Step status: {data['status']}")
        print(f"Step result: {data['result'][:100]}...")  # Print first 100 chars of result
    
    research_topic = "The impact of artificial intelligence on job markets in the next decade"
    final_report = research_and_write_report(research_topic, print_callback)
    print("Final Report:")
    print(final_report)
