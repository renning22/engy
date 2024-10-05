# Engy

## Overview

Engy is a lightweight development tool that generates fully functional web applications from simple natural language prompts. It's designed for developers who want to rapidly prototype and build applications, taking them from 0 to 80% completion using just natural language descriptions.

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

3. Run Engy:
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
engy clone /path/to/my_app
```

## Examples

[TODO: Add examples of apps created with Engy, including screenshots and brief descriptions]

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