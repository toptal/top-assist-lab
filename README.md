# Nur AI
The self-actualizing documentation Chat Bot that heals its knowledge gaps
as naturally as a ray of light - with AI
[Custom GPT to discuss the code base](https://chat.openai.com/g/g-zKBLXtfrD-shams-nur)

## Problem
Organizational knowledge is hard to find and keep updated.
 Accessing information is challenging for busy individuals or those with neuro-divergent brains.
 Current solutions lead to outdated documentation and inaccessible information.

## Solution
Nur AI utilizes generative AI to identify and fill knowledge gaps.
Offers both text and in the future audio access to documentation.
Currently in extensive MVP testing.

## Business model
Open Source free to use -
Apache-2 license

Easy onboarding, reach out if you need support.

## Team
- [Roland Younes](https://www.linkedin.com/in/rolanday/): With 24 years in tech, including 10 years in tech management and software development, Roland brings a wealth of experience alongside a 2-year deep dive into Gen AI and Python.

- [Charbel Abou Younes](https://www.linkedin.com/in/charbelay/): Charbel, a software development virtuoso, brings his AWS expertise and Adobe Commerce proficiency to the fore, ensuring robust and scalable cloud solutions.

- You...? Interested in AI, documentation, and making a difference? Join us! Whether it’s for a chat, a feature request, or to contribute, we're open to your ideas and contributions.

# Testing

## pytest

Unit tests are located inside `tests` directory.

Execution with coverage report:
* fail if coverage is below 0% (`--cov-fail-under`)
* location of code to be included in the coverage report: `--cov=relative_path/`

```
poetry run pytest --cov-fail-under=0 --cov=file_system/
```

## Feature list

### Done:
#### Capabilities
- Learns from your confluence
- Chats with you in slack based on the knowledge in confluence
- Identifies knowledge gaps
- Asks questions on Slack to collect knowledge
- Capture :checkmark: reaction
  - Summarise the conversation and add document to confluence
- Capture :bookmark: reaction
  - Add the conversation to confluence
- gamification (leader board)
    - light seekers ( people who ask questions)
    - revealers ( people who ask undocumented questions)
    - luminaries ( people who contribute to knowledge gathering)
- visualize documentation in 3D space

### Todo:

- Space management
  - Retrieve documentation updates nightly
  - Delete documentation scope (Space) from vector

- Advanced Knowledge gap recovery gamification
  - Collects the top unanswered questions by theme
  - Identify the people who asked them
  - We invite to the Trivia channel the users who asked the. questions and the domain experts
  - The bot asks the questions, people answer and discuss till satisfaction
  - People thumbs up the good contributions
  - The bot collects the conversation data and based on it:
  - Proposes new documents
  - Upgrades the leaderboard with the top contributors

- Refactor
  - Move everything network to a network package
    - organize network functions into objects

- Enable function calling for context retrieval

- Build an algorythm that uses AI to manage retrieval cleanup and volume optimization locally

- Chunk to embed and context and providing document ids from metadata but keep including full documents in context

- Add credibility rating to database



## Setup
### prerequisites:
- sqlite3
- Python 3.12
- poetry
- pycharm

### Managing python version with `asdf`

Install `asdf` from https://asdf-vm.com/

```
# install plugin for python version management
asdf plugin add python

# install python version declared in .tool-versions
asdf install python

# test it
python --version
Python 3.12.2
```

The version that `asdf` will use for the current project is declared in `.tool-versions` file.

## Configuration
1. Rename credentials_example.py to credentials.py & .env.example to .env
2. Follow the instructions in the files to fill in the values


### Run Top-Assist

````
git clone https://github.com/toptal/top-assist
cd top-assist
poetry install
PYTHONPATH=. poetry run python main.py
````

`PYTHONPATH=. poetry run python main.py` (for the menu operations)

`PYTHONPATH=. poetry run python api/endpoint.py` (API / uvicorn web server)

Refer to the ./documentation/slack_app_manifest_installation_guide.md for slack bot setup

`PYTHONPATH=. poetry run python slack/bot.py` (slack bot stream listener)

### Run DBs

Top Assist uses two databases: `postgresql` and `chroma`.  
Please be sure that you set all the required environment variables in the `.env` file in `# Database` section.
To run the databases, you can use docker-compose

```
docker composer up
poetry run alembic upgrade head     # to setup PostgreSQL database
```


### DB Migrations

1) Import the model in `alembic/env.py` and run:
```
poetry run alembic revision --autogenerate -m "Add my new model"
```
Alembic will detect the changes in the models/tables and create a new migration file.  
Be aware that it can remove empty indexes/fields.  
If you need to have control over the migration you can remove the `--autogenerate` flag and write the migration manually.  


2) Apply the migration:  
`poetry run alembic upgrade head`

3) To rollback last N migrations run:  
`poetry run alembic downgrade -N`


## Network traffic

1. Outgoing to Open AI API (for Embeds and completion)
2. Two-way to slack api and from slack stream (for receiving and sending messages)
3. Outgoing anonymized telemetry data to Chroma that will be disabled soon
4. Outgoing to confluence API for (document management)

## Technologies
- chromadb
- slack
- confluence
- persis-queue
## Technologies in consideration
- aws
- azure
- pinocone
- celery
- rabbitmq
- postgreaql

## Documentation
Refer to the ./documentation folder for project documentation.

