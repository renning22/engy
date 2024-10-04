"""
cd crewai
pip install -e .[tools] dash-bootstrap-components pandas dash dash-ag-grid langfuse langchain_anthropic
"""

import io
import os
import pickle
import datetime

import dash_bootstrap_components as dbc
import pandas as pd
from crewai import Agent, Crew, Task
from langchain_core.agents import AgentFinish
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from dash import Dash, State, Input, Output, callback, dash_table, dcc, html
from langchain_anthropic import ChatAnthropic
import dash_ag_grid as dag
from dash.exceptions import PreventUpdate

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


def step_callback(step_output):
    step_outputs.append(step_output)
    with open('step_outputs.pickle', 'wb') as f:
        pickle.dump(step_outputs, f)

    global step_outputs_timestamp
    step_outputs_timestamp = datetime.datetime.now()


def create_crew(input_search_icp, input_seed_search_query):
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
        tools=[search_tool]
    )

    sales = Agent(
        role='Senior Sales Representative',
        goal='Search internet and major social websites and find out given person contact information',
        backstory="""You work at a startup as a sales. You are farmilier with major social websites and good finding and contacting people.""",
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

    task2 = Task(
        description="""Find one contact for each of these comapnies.
Contacts are better titles of Finance, Operations and Revenue Operations as well as Founder(s), CEO.

If you can find their linkedin page URL, also add to the table.
""",
    expected_output="""Return in CSV format with exact header [first_name, last_name, job_title, company_full_name, official_website, linkedin_page]

The output must follow:
```csv
first_name, last_name, job_title, company_full_name, official_website, linkedin_page
...
...
```
    """,
        agent=sales
    )

    task3 = Task(
        description="""Try best to search and make up contact's "email address".

You may:
1. Do more search using search tool.
2. Scraping their personal_website
3. Scraping company official_website.
4. Don't scrape linkedin page (since the site is blocked).

If not found, try best to make up one, e.g. {first_name}{last_name}@gmail.com        
""",
    expected_output="""Return in CSV format with exact header [first_name, last_name, job_title, email_address, linkedin_page, personal_website, company_full_name, official_website]

The output must follow:
```csv
first_name, last_name, job_title, email_address, linkedin_page, personal_website, company_full_name, official_website
...
...
```
    """,
        agent=sales
    )

    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[contact_finder, sales],
        tasks=[task1, task2, task3],
        step_callback=step_callback,
        verbose=2,  # You can set it to 1 or 2 to different logging levels
        output_log_file='1.log',
    )
    return crew


def run_agent(input_search_icp, input_seed_search_query):
    global step_outputs
    step_outputs = []

    crew = create_crew(input_search_icp, input_seed_search_query)
    result = crew.kickoff()
    print("###################### Result:")
    print(result)


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


def populate_layout():
    return dbc.Container([
        html.H1('Company-Search Agent Workflow 🕵️🕵️🕵️'),
        dbc.Label('Search ICP: '),
        dbc.Input(value=search_icp, id='input_search_icp'),
        dbc.Label('Seed Search Query: '),
        dbc.Input(value=seed_search_query, id='input_seed_search_query'),
        dbc.Button('Run Agent Workflow', id='run_workflow', n_clicks=0),
        dbc.Label('Last Update: '),
        dcc.Input(str(step_outputs_timestamp),
                  id='last_update_timestamp', readOnly=True),
        html.Hr(),
        dbc.Container(
            id='action_log_container',
        ),
        dash_table.DataTable(None, id='tbl'),
        dcc.Interval(
            id='interval_component',
            interval=500,  # in milliseconds
            n_intervals=0
        )
    ])


app.layout = populate_layout


@callback(Input('run_workflow', 'n_clicks'),
          State('input_search_icp', 'value'),
          State('input_seed_search_query', 'value'),
          prevent_initial_call=True)
def click_run_workflow_button(input_search_icp, input_seed_search_query, n_clicks):
    run_agent(input_search_icp, input_seed_search_query)
    return None


@callback(Output('action_log_container', 'children'),
          Output('last_update_timestamp', 'value'),
          Input('interval_component', 'n_intervals'),
          State('last_update_timestamp', 'value'))
def update_action_log(n, input_last_update):
    if input_last_update == str(step_outputs_timestamp):
        raise PreventUpdate

    counter = 0
    ret = []
    for output in step_outputs:
        if isinstance(output, AgentFinish):
            st = f"""{output.type}({list(output.return_values.keys())})"""
            ret.append(html.Div(st))

            try:
                final_output = output.return_values['output']
                final_output = final_output.split('```csv')[1]
                final_output = final_output.split('```')[0]
            except:
                ret.append(html.Div('Parse CSV error'))
                continue

            df = pd.read_csv(io.StringIO(final_output))
            print('DataFrame')
            print(df)

            columnDefs = []
            for column in df:
                if column in ['linkedin_page', 'official_website']:
                    columnDefs.append({
                        "field": column,
                        "cellRenderer": "markdown",
                        "valueFormatter": {"function": """params.value == null ? '' : `<a href="${params.value}" target="_blank">${params.value}</a>`"""},
                    })
                elif column in ['email_address']:
                    columnDefs.append({
                        "field": column,
                        "cellRenderer": "markdown",
                        "valueFormatter": {"function": """params.value == null ? '' : `<a href="mailto:${params.value}" target="_blank" style="color:red;">${params.value}</a>`"""},
                    })
                else:
                    columnDefs.append({'field': column})

            table_id = f'table-{counter}'
            download_button_id = f"csv-download-button-{counter}"

            table = dag.AgGrid(
                rowData=df.to_dict("records"),
                columnDefs=columnDefs,
                id=table_id,
                columnSize="sizeToFit",
                csvExportParams={
                    "fileName": f"{table_id}.csv",
                },
            )

            ret.append(table)
            ret.append(html.Button("Download CSV",
                       id=download_button_id, n_clicks=0))
            ret.append(html.Hr())

            @callback(
                Output(table_id, "exportDataAsCsv"),
                Input(download_button_id, "n_clicks"),
            )
            def click_download_as_csv(n_clicks):
                if n_clicks:
                    return True
                return False

            counter = counter + 1
        else:
            assert isinstance(output, list)
            for action, observation in output:
                st = f"""{action.type}(tool='{action.tool}', tool_input='{action.tool_input}', observation={len(observation)})"""
                ret.append(html.Div(st))
                counter = counter + 1

    return ret, str(step_outputs_timestamp)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
