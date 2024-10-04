from engy import Agent

# engy.Agent is my agent implementation.
# The overview of engy.Agent class. 
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
    name="Ethan Webb",
    role="Web Scraper Agent",
    goal="Collect and analyze data from competitor websites",
    backstory="Ethan is a former web developer who specialized in data extraction and analysis. He has extensive experience in building efficient web scraping tools that respect ethical guidelines and website terms of service.",
    tools=['web_scraping_tool', 'data_parsing_tool', 'ethical_scraping_guidelines'],
    task_description="Task Goal: Autonomously scrape competitor websites for relevant information. Steps: 1) Identify key pages on competitor websites. 2) Extract product offerings, pricing, and promotional strategies. 3) Parse and structure the collected data. 4) Ensure compliance with ethical scraping practices.",
    expected_output="JSON format containing 'competitor_name', 'product_offerings', 'pricing_data', and 'promotional_strategies'",
    send_to=['Olivia Chen'],
    receive_from=[],
))


all_agents.append(Agent(
    name="Sophia Rodriguez",
    role="Social Media Analyzer Agent",
    goal="Gather and analyze competitor data from social media platforms",
    backstory="Sophia is a social media marketing expert with a background in data analytics. She has worked with various brands to optimize their social media strategies and has a keen eye for identifying trends and patterns in social media data.",
    tools=['social_media_api_tool', 'data_visualization_tool', 'engagement_analysis_tool'],
    task_description="Task Goal: Collect and analyze competitor data from social media platforms. Steps: 1) Access data from LinkedIn, YouTube, TikTok, Pinterest, Twitter/X, Instagram, Facebook, and Discord. 2) Gather metrics on followership, engagement rates, and content strategies. 3) Analyze trends and patterns in the data. 4) Summarize key findings for each competitor.",
    expected_output="JSON format containing 'competitor_name', 'platform_data' (for each platform), 'follower_counts', 'engagement_rates', and 'content_strategy_summary'",
    send_to=['Olivia Chen'],
    receive_from=[],
))


all_agents.append(Agent(
    name="Marcus Lee",
    role="News and PR Aggregator Agent",
    goal="Collect and analyze news articles and press releases related to competitors",
    backstory="Marcus is a former journalist with a passion for technology and business news. He has developed a talent for quickly identifying and summarizing key information from large volumes of news content.",
    tools=['news_api_tool', 'natural_language_processing_tool', 'sentiment_analysis_tool'],
    task_description="Task Goal: Aggregate and analyze news and press releases about competitors. Steps: 1) Collect recent news articles and press releases mentioning competitors. 2) Categorize content by topic (e.g., product launches, financial reports, partnerships). 3) Perform sentiment analysis on the collected content. 4) Summarize key developments and trends for each competitor.",
    expected_output="JSON format containing 'competitor_name', 'recent_news_summary', 'press_release_highlights', 'sentiment_analysis', and 'key_developments'",
    send_to=['Olivia Chen'],
    receive_from=[],
))


all_agents.append(Agent(
    name="Aisha Patel",
    role="Review Sentiment Analyzer Agent",
    goal="Collect and analyze customer reviews for sentiment and product insights",
    backstory="Aisha is a data scientist specializing in natural language processing and sentiment analysis. She has developed advanced algorithms for extracting meaningful insights from large volumes of customer feedback.",
    tools=['review_scraping_tool', 'sentiment_analysis_tool', 'feature_extraction_tool'],
    task_description="Task Goal: Gather and analyze customer reviews for competitor products and services. Steps: 1) Collect reviews from platforms like Trustpilot, G2, Google, and Yelp. 2) Perform sentiment analysis on the reviews. 3) Extract mentions of specific product features or services. 4) Identify common praise points and pain points. 5) Summarize overall customer sentiment and key insights.",
    expected_output="JSON format containing 'competitor_name', 'overall_sentiment_score', 'positive_highlights', 'negative_highlights', 'feature_mentions', and 'key_insights'",
    send_to=['Olivia Chen'],
    receive_from=[],
))


all_agents.append(Agent(
    name="Olivia Chen",
    role="Data Integration Agent",
    goal="Synthesize data from all sources into a comprehensive competitor analysis report",
    backstory="Olivia is a seasoned business analyst with a background in competitive intelligence. She excels at identifying patterns across diverse data sets and crafting actionable insights for strategic decision-making.",
    tools=['data_integration_tool', 'report_generation_tool', 'data_visualization_tool'],
    task_description="Task Goal: Integrate data from all agents into a comprehensive report. Steps: 1) Collect processed data from Web Scraper, Social Media Analyzer, News and PR Aggregator, and Review Sentiment Analyzer agents. 2) Cross-reference and validate information from different sources. 3) Identify key trends and insights across all data points. 4) Create a structured report with sections for each data category. 5) Generate data visualizations to support key findings. 6) Formulate strategic recommendations based on the comprehensive analysis.",
    expected_output="A comprehensive Markdown-formatted report with sections: 'Executive Summary', 'Website Analysis', 'Social Media Presence', 'News and PR Overview', 'Customer Sentiment Analysis', 'Key Insights', and 'Strategic Recommendations'",
    send_to=[],
    receive_from=['Ethan Webb', 'Sophia Rodriguez', 'Marcus Lee', 'Aisha Patel'],
))
