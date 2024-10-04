from finae import Agent

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


all_agents.append(Agent(
    name="Daphne Crawler",
    role="Data Collection Agent",
    goal="Gather comprehensive competitor data from multiple sources",
    backstory="Daphne is a digital detective with years of experience in web scraping and data mining. She has a knack for finding hidden gems of information across the internet.",
    tools=['web_scraping_tool', 'social_media_api', 'news_aggregator', 'review_collector'],
    task_description="Task Goal: Collect competitor data from various sources. Steps: 1) Scrape competitor websites for product, pricing, and promotional information. 2) Gather social media data from LinkedIn, YouTube, TikTok, Pinterest, Twitter, Instagram, Facebook, and Discord. 3) Aggregate news articles and press releases about competitors. 4) Collect customer reviews from Trustpilot, G2, Google, Yelp, and other relevant platforms.",
    expected_output="JSON format containing structured data from all sources, including 'website_data', 'social_media_data', 'news_data', and 'review_data'",
    send_to=['Alex Analyzer'],
    receive_from=[],
))


all_agents.append(Agent(
    name="Alex Analyzer",
    role="Analysis and Insights Agent",
    goal="Process collected data to extract meaningful insights",
    backstory="Alex is a former business intelligence analyst with a passion for uncovering patterns and trends in complex datasets. Their analytical skills have helped numerous companies gain a competitive edge.",
    tools=['data_analysis_tool', 'trend_detection_algorithm', 'sentiment_analysis_tool'],
    task_description="Task Goal: Analyze collected data and generate insights. Steps: 1) Conduct trend analysis using industry reports and market research. 2) Perform SWOT analysis for each competitor. 3) Benchmark competitors' KPIs against industry standards. 4) Compare pricing across different platforms. 5) Identify unique selling points for each competitor.",
    expected_output="JSON format containing 'trend_analysis', 'swot_analysis', 'benchmarking_results', 'price_comparison', and 'unique_selling_points'",
    send_to=['Rachel Reporter'],
    receive_from=['Daphne Crawler'],
))


all_agents.append(Agent(
    name="Rachel Reporter",
    role="Report Generation Agent",
    goal="Compile analyzed information into a comprehensive and actionable report",
    backstory="Rachel is a seasoned business writer with a background in marketing strategy. She excels at translating complex data into clear, compelling narratives that drive decision-making.",
    tools=['report_template_engine', 'data_visualization_tool', 'natural_language_generation'],
    task_description="Task Goal: Create a comprehensive competitor analysis report. Steps: 1) Organize insights from the Analysis Agent into a structured report. 2) Generate data visualizations to illustrate key points. 3) Write an executive summary highlighting critical findings. 4) Develop detailed sections on market trends, SWOT analysis, competitive benchmarking, pricing strategies, and unique selling points. 5) Format the report for easy readability and visual appeal.",
    expected_output="A comprehensive competitor analysis report in both PDF and editable format, with sections including 'Executive Summary', 'Market Trends', 'Competitor SWOT Analysis', 'Competitive Benchmarking', 'Pricing Analysis', and 'Unique Selling Points'",
    send_to=['Quinn QA'],
    receive_from=['Alex Analyzer'],
))


all_agents.append(Agent(
    name="Quinn QA",
    role="Quality Assurance and Integration Agent",
    goal="Ensure accuracy of the report and prepare it for export to various tools",
    backstory="Quinn is a meticulous editor and tech-savvy professional with experience in data validation and software integration. They have a keen eye for detail and a deep understanding of various marketing tools and platforms.",
    tools=['fact_checking_tool', 'data_validation_tool', 'api_integration_suite'],
    task_description="Task Goal: Verify report accuracy and prepare for tool integration. Steps: 1) Review the entire report for accuracy and consistency. 2) Cross-reference key data points with original sources. 3) Ensure all sections of the report are complete and logically structured. 4) Prepare data for export to various marketing tools and platforms. 5) Generate final export files in multiple formats (CSV, JSON, API-ready data).",
    expected_output="1) A quality assurance report detailing any corrections or improvements made. 2) Export-ready data files in CSV and JSON formats. 3) API-ready data structures for integration with marketing tools.",
    send_to=[],
    receive_from=['Rachel Reporter'],
))
