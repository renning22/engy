# engy

## Overview

Engy is a lightweight dev tool to generate fully working web apps from simple prompts.

It's useful for developers who can create apps from 0 to 80% in natural language as a starting point.

Behind, it's an agentic workflow do all the work including generaring design docs, back-end python server, front-end html, dockerfile, README.md. 


## Quick Start

Install
```
pip install engy
```

Generate new app from scrapts.
```bash
mkdir my_app && cd my_app
edit input.txt  # Your app idea, e.g. "create a calculator"
engy
```

To run the generated app, there will be a generated "run.sh" include everything you need.
```bash
bash run.sh
```

Add feature to your app by prompts.
```bash
cd my_app
edit feature.txt  # Feature you want to add, e.g. "make the calculator support calculus and algebra"
engy feature
```

Use prompts to edit front-end.
```bash
engy frontend
# Enter prompts in terminal
```

Use prompts to edit back-end.
```bash
engy backend
# Enter prompts in terminal
```

Clone a new app from generated one.
```bash
mkdir my_app_2 && cd my_app_2
edit input.txt  # 
engy clone /path/to/my_app
```

## Examples

TODO

## Install locally for dev

```
git clone https://github.com/renning22/engy.git
cd engy
pip install -e .
```

## Contribute

Contact @renning22 and @mincomp.
