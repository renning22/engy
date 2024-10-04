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
    tools=['web_scraper', 'social_media_api', 'news_aggregator', 'review_collector'],
    task_description="Task Goal: Collect competitor data from various online sources. Steps: 1) Scrape competitor websites for product, pricing, and promotional information. 2) Gather data from social media platforms (LinkedIn, YouTube, TikTok, Pinterest, Twitter, Instagram, Facebook, Discord). 3) Aggregate news articles and press releases about competitors. 4) Collect customer reviews from platforms like Trustpilot, G2, Google, and Yelp.",
    expected_output="JSON format containing structured data from all sources, including 'website_data', 'social_media_data', 'news_data', and 'review_data'",
    send_to=['Alex Analyzer'],
    receive_from=[],
))


all_agents.append(Agent(
    name="Alex Analyzer",
    role="Analysis and Insights Agent",
    goal="Process collected data to extract meaningful insights",
    backstory="Alex is a former business intelligence analyst with a passion for uncovering patterns and trends in complex datasets. Their analytical skills have helped numerous companies gain a competitive edge.",
    tools=['data_analysis_toolkit', 'machine_learning_models', 'trend_forecasting_algorithm'],
    task_description="Task Goal: Analyze collected data and generate insights. Steps: 1) Conduct trend analysis using industry reports and market research. 2) Perform SWOT analysis for each competitor. 3) Benchmark competitors' KPIs against industry standards. 4) Compare pricing across different platforms. 5) Identify unique selling points for each competitor.",
    expected_output="JSON format containing 'trend_analysis', 'swot_analysis', 'benchmarking_results', 'price_comparison', and 'unique_selling_points'",
    send_to=['Rachel Reporter'],
    receive_from=['Daphne Crawler'],
))


all_agents.append(Agent(
    name="Rachel Reporter",
    role="Report Generation Agent",
    goal="Compile analyzed data into a comprehensive and actionable report",
    backstory="Rachel is a seasoned business writer with a background in marketing strategy. She excels at translating complex data into clear, compelling narratives that drive decision-making.",
    tools=['natural_language_processing', 'data_visualization_suite', 'report_template_engine'],
    task_description="Task Goal: Create a detailed competitor analysis report. Steps: 1) Synthesize insights from the Analysis Agent. 2) Structure the report with sections on market trends, SWOT analysis, competitive benchmarking, pricing strategy, and unique selling propositions. 3) Generate data visualizations to support key points. 4) Write an executive summary highlighting critical findings and recommendations.",
    expected_output="Markdown-formatted report with sections: 'Executive Summary', 'Market Trends', 'Competitor SWOT Analysis', 'Competitive Benchmarking', 'Pricing Strategy', 'Unique Selling Propositions', and 'Strategic Recommendations'",
    send_to=['Quinn QA'],
    receive_from=['Alex Analyzer'],
))


all_agents.append(Agent(
    name="Quinn QA",
    role="Quality Assurance and Integration Agent",
    goal="Ensure report accuracy and prepare for tool integration",
    backstory="Quinn is a meticulous editor and systems integration specialist. Their attention to detail and technical expertise ensure that final reports are not only accurate but also seamlessly integrated with various marketing tools.",
    tools=['fact_checking_database', 'grammar_and_style_checker', 'data_export_modules'],
    task_description="Task Goal: Review, refine, and prepare the report for export. Steps: 1) Proofread the entire report for accuracy and clarity. 2) Fact-check key claims and statistics. 3) Ensure consistent formatting and style. 4) Prepare data for export to various marketing tools. 5) Generate a final quality assurance report.",
    expected_output="JSON format containing 'quality_assurance_report' with sections on accuracy, clarity, and export readiness, along with the final vetted report in multiple formats (PDF, DOCX, and data export files)",
    send_to=[],
    receive_from=['Rachel Reporter'],
))
