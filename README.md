# Engy

## Overview

Engy is a lightweight development tool that generates fully functional web applications from simple natural language prompts. It's designed for developers who want to rapidly prototype and build applications, taking them from 0 to ~80% completion using just natural language descriptions.

Engy utilizes an agentic workflow to automate the entire development process, including:
- Generating design documents
- Creating backend Python servers
- Developing frontend HTML
- Producing Dockerfiles
- Crafting README files

## Quick Start

### Installation

```bash
pip install engy
```

### Generate a New App

1. Create a new directory for your app:
   ```bash
   mkdir my_app && cd my_app
   ```

2. Create an `input.txt` file with your app idea:
   ```bash
   echo "create a calculator" > input.txt
   ```

3. Add your API keys to the `.env` file:
   ```bash
   echo "ANTHROPIC_API_KEY=xxx" > .env
   ```
   The default model is `claude-3-5-sonnet`, so by default you only need `ANTHROPIC_API_KEY`.
   To use other models, set `MODEL=xxx` in the `.env` file. See `llm.py` and the `litellm` backend for supported models.

4. Run Engy:
   ```bash
   engy
   ```

### Run the Generated App

Engy creates a `run.sh` script with everything you need to run your app:

```bash
bash run.sh
```

### Add Features to Your App

1. Navigate to your app directory:
   ```bash
   cd my_app
   ```

2. Create a `feature.txt` file with the desired feature:
   ```bash
   echo "make the calculator support calculus and algebra" > feature.txt
   ```

3. Run Engy's feature addition:
   ```bash
   engy feature
   ```

### Edit Frontend or Backend

Use prompts to modify your app's frontend or backend:

```bash
engy frontend
# Enter prompts in the terminal
```

```bash
engy backend
# Enter prompts in the terminal
```

### Clone an Existing App

To create a new app based on an existing one:

```bash
mkdir my_app_2 && cd my_app_2
echo "make change ..." > input.txt
engy clone /path/to/my_app
```

## Examples

Engy comes with a wide range of example projects to help you get started and understand its capabilities. Here's a selection of examples organized by category:

### Agentic Workflows
- [Simple Agentic Example](examples/agentic/simple)
- [Stock News Agent](examples/agentic/stock_news)

### Airtable Integration
- [Edit Airtable](examples/airtable/edit_airtable)
- [Edit Airtable with Dashboard](examples/airtable/edit_airtable_dash)
- [Product Roadmap](examples/airtable/product_roadmap)

### Basic Tools
- [Airtable CRM](examples/basic_tools/airtable_crm_1)
- [Calculator](examples/basic_tools/calculator)
- [Docker Containers Manager](examples/basic_tools/docker_containers)
- [Document Summary Agent](examples/basic_tools/doc_summary_agent)
- [Email Summary Agent](examples/basic_tools/email_summary_agent)
- [Expense Tracker](examples/basic_tools/expense_tracker)
- [Invoice Creator](examples/basic_tools/invoice_creator)
- [Kubernetes Pods Manager](examples/basic_tools/k8s_pods)
- [Trip Planner (Hawaii)](examples/basic_tools/plan_a_trip_hawaii)
- [Sales Revenue Dashboard](examples/basic_tools/sales_revenue_dashboard)
- [Text Diff Tool](examples/basic_tools/text_diff)
- [Video Format Converter](examples/basic_tools/video_format_converter)
- [Voice Note Taker](examples/basic_tools/voice_note_taker)
- [Web3 Explorer](examples/basic_tools/web3_explorer_1)
- [Weeks in Life Visualizer](examples/basic_tools/weeks_in_life)
- [Meal Planner](examples/basic_tools/what_to_eat)
- [YouTube Video Manager](examples/basic_tools/yt_videos)

### Customer Experience Insights
- [CX Insights Experiment](examples/cx_insights/exp_1)
- [Customer Insight Generator](examples/cx_insights/insight_1)
- [Review Data Analyzer](examples/cx_insights/review_data_1)

### Demo Applications
- [Account Manager](examples/demo/account_manager)
- [PDF Merger](examples/demo/pdf_merger)
- [Web Scraper](examples/demo/scraper_1)

### Retool Integration
- [Retool Account Manager](examples/retool/account_manager)
- [Customer Insights Dashboard](examples/retool/customer_insights_dashboard)
- [Food Delivery Tracker](examples/retool/food_delivery_tracker)
- [SLA Dashboard](examples/retool/sla_dashboard)

To explore these examples, navigate to the respective folders in the `examples` directory of the Engy repository. Each example includes its own README and source code to help you understand how it was built using Engy.

## Local Development Setup

To install Engy locally for development:

```bash
git clone https://github.com/renning22/engy.git
cd engy
pip install -e .
```

## Contributing

We welcome contributions to Engy! If you're interested in contributing, please contact:
- @renning22
- @mincomp

[TODO: Add more detailed contribution guidelines, including how to submit pull requests, coding standards, and the development process]

## License

[TODO: Add license information]

## Support

[TODO: Add information on how to get support, such as linking to documentation, FAQ, or community forums]