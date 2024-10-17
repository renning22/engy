# 🚀 Engy: Your AI-Powered App Generator

## 🌟 Welcome to the Post-LLM Era of App Development

In a world transformed by Large Language Models, we'll never write anything from scratch again. Enter Engy, your AI companion that's revolutionizing the way we create web applications! 🤖💻✨ Whether you're a seasoned developer or a curious innovator, Engy empowers you to turn your ideas into fully-functional web apps with Python backends and HTML/JavaScript frontends - all without starting from a blank slate.

Say goodbye to the days of painstakingly coding every line. With Engy, it's like having a team of developers at your fingertips, ready to materialize your vision into reality. From simple tools to complex data analysis applications, Engy understands your intent and does the heavy lifting for you.

### 🛠️ Versatile App Generation
Engy can help you create a variety of applications, including (but not limited to):
- 📝 Productivity tools and task managers
- 🗂️ Data organization and management systems
- 🌐 Web scrapers and data collectors
- 📊 Simple data visualization tools


## 🚦 Quick Start Guide

### 🔧 Installation
Get started with:
```bash
pip install engy
```

### 🎉 Create Your App

1. Set up your project:
   ```bash
   mkdir my_awesome_app && cd my_awesome_app
   ```

2. Describe your app idea:
   ```bash
   echo "create a calculator" > input.txt
   ```

3. Add your API key:
   ```bash
   echo "ANTHROPIC_API_KEY=your_super_secret_key" > .env
   ```

   The default model is `claude-3.5-sonnet`. You can switch to any model, e.g. gpt-4 by adding the following to your `.env` file:
   ```bash
   echo "MODEL=gpt-4" >> .env
   echo "OPENAI_API_KEY=your_openai_api_key" >> .env
   ```

4. Let Engy work its magic:
   ```bash
   engy
   ```

### 🏃‍♂️ Run Your New App
Engy provides a ready-to-go script:
```bash
bash run.sh
```

### 🌈 Enhance Your App with More Features

1. Describe your new feature:
   ```bash
   echo "make the calculator support calculus and algebra" > feature.txt
   ```

2. Let Engy implement it:
   ```bash
   engy feature
   ```

### 🎨 Fine-tune Your Backend and Frontend
Tweak your app's functionality or user interface:

```bash
engy backend
# Enter prompts to optimize your data handling or add new processing features
```

```bash
engy frontend
# Enter prompts to enhance your UI or add new interactive elements
```

### 🔧 Refactor Your App
To refactor your app's frontend and backend into modular files:

```bash
engy split
```

This command will reorganize your code structure for better maintainability and scalability.

### 🧬 Clone an Existing App
To create a new app based on an existing one:

```bash
mkdir my_app_2 && cd my_app_2
echo "new changes..." > input.txt
engy clone /path/to/my_app
```

## 🌟 Example Showcase

Engy comes with a wide range of example projects to help you get started and understand its capabilities. Here's a selection of examples organized by category:


### 🎨 Demo Applications

- [Account Manager](examples/demo/account_manager)
- [PDF Merger](examples/demo/pdf_merger)
- [Web Scraper](examples/demo/scraper_1)


### 🛠️ Basic Tools

- [Airtable CRM](examples/basic_tools/airtable_crm_1)
- [Calculator](examples/basic_tools/calculator)
- [Daughter School Planner](examples/basic_tools/daughter_school)
- [Docker Containers Manager](examples/basic_tools/docker_containers)
- [Document Summary Agent](examples/basic_tools/doc_summary_agent)
- [Dota 2 Hero Agent](examples/basic_tools/dota2_hero_agent)
- [Email Summary Agent](examples/basic_tools/email_summary_agent)
- [Expense Tracker](examples/basic_tools/expense_tracker)
- [GCP Tool](examples/basic_tools/gcp_tool_1)
- [Invoice Creator (Version 1)](examples/basic_tools/invoice_creator)
- [Invoice Creator (Version 2)](examples/basic_tools/invoice_creator_2)
- [Kubernetes Pods Manager](examples/basic_tools/k8s_pods)
- [Trip Planner (Hawaii)](examples/basic_tools/plan_a_trip_hawaii)
- [Sales Revenue Dashboard](examples/basic_tools/sales_revenue_dashboard)
- [Text Diff Tool](examples/basic_tools/text_diff)
- [Video Format Converter](examples/basic_tools/video_format_converter)
- [Voice Note Taker](examples/basic_tools/voice_note_taker)
- [Web3 Explorer (Version 1)](examples/basic_tools/web3_explorer_1)
- [Web3 Explorer (Version 2)](examples/basic_tools/web3_explorer_2)
- [Weeks in Life Visualizer](examples/basic_tools/weeks_in_life)
- [Meal Planner (Version 1)](examples/basic_tools/what_to_eat)
- [Meal Planner (Version 2)](examples/basic_tools/what_to_eat_2)
- [YouTube Video Manager](examples/basic_tools/yt_videos)


### 🚀 Advanced Examples

- [Account Manager](examples/advance/account_manager)
- [Customer Insights Dashboard](examples/advance/customer_insights_dashboard)
- [Customer Experience Insights](examples/advance/cx_insights)
- [Edit Airtable](examples/advance/edit_airtable)
- [Edit Airtable with Dashboard](examples/advance/edit_airtable_dash)
- [Food Delivery Tracker](examples/advance/food_delivery_tracker)
- [Product Roadmap](examples/advance/product_roadmap)
- [SLA Dashboard](examples/advance/sla_dashboard)

## 🛠️ Contribute

This repo is created and mainly maintained by two passionate engineers:

- @renning22: ex-MLE at Pony.AI, ex-Googler
- @mincomp: MLE at ScaleAI, ex-Meta, ex-Uber

They envision and practice that tedious low-level coding work can be replaced by AI.

Any contribution is welcomed! Create issue/PR and at us!

## 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.


## 🆘 Need Help with Your App?

If you're having trouble generating your app or encountering any issues, don't hesitate to reach out! Feel free to open an issue on our GitHub repository or contact us directly at renning22@gmail.com. We're very happy to pilot you and give help. We're here to help you bring your app ideas to life with Engy!
