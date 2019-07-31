# Elija &middot; Ask your Repository Backend API  
[![Coverage Status](https://coveralls.io/repos/github/hpi-sam/ask-your-repository-api/badge.svg)](https://coveralls.io/github/hpi-sam/ask-your-repository-api)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

This repo is part of the "Ask your Repository" Bachelor project containing the following repos:  
- [Elija - Ask your Repository Backend API](https://github.com/hpi-sam/ask-your-repository-api)  
- [Jona - Ask your Repository Web Frontend](https://github.com/hpi-sam/ask-your-repository-web)  
- [Tobito - Ask your Repository Dialogflow Adapter](https://github.com/hpi-sam/ask-your-repository-dialogflow-adapter)  
- [Ask your Repository Docker Deployment](https://github.com/hpi-sam/ask-your-repository-docker)  


# Setup service
- If you have docker installed you can simply run `docker-compose up -d` and skip the rest of this readme.
- **Install Python 3.7**:
  - On Windows:
    - Click: Add path
    - At the end of installation allow usage of paths longer than 260 characters
    - See: [Setup Python](https://docs.python.org/3/using/windows.html)
  - On Unix systems its highly recommended to use [pyenv](https://github.com/pyenv/pyenv#installation) instead for this as it makes swapping python versions much easier.  
  You can use the installer from [here](https://github.com/pyenv/pyenv-installer) for easy installation.

- **Installing dependencies**:
  -Setup Poetry:
    - [Install Poetry](https://poetry.eustace.io/docs/#system-requirements)
    - Install dependencies via: `poetry install`

  - Copy .env.example into new .env file
  - It's highly recommended you have docker installed it makes environment setup much easier: https://www.docker.com/get-started
  - Install Neo4j
    - Neo4J is our GraphDB you can find more info and an install guide on it here: https://neo4j.com/
    - To run tests you need a neo4j installation on the ports specified in `.env.testing`
    - To simply run the application locally I recommend seting up a docker container with neo4j with this command: 
      ```
      docker run \
      --publish=7474:7474 --publish=7687:7687 \
      --volume=$HOME/neo4j/data:/data \
      --volume=$HOME/neo4j/logs:/logs \
      neo4j:3.0
      ```

  - Install Elasticsearch
    - [Setup Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
    - Don't forget to set JAVA_HOME path to the path of java jdk
    - You can setup a local ES docker container with this command:
      ```
      docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:6.5.2
      ```

- Setup elasticsearch development and testing
  - Rename config directory to config.development in your elasticsearch installation directory
  - Copy the contents of elasticsearch.example.yml in this repository into elasticsearch.yml in config.development
  - Make a new directory named config.test and copy the contents of config.development into it
  - Edit the elasticsearch.yml by replacing every occurence of development with test and **change the port to 9400**
  - Start both services by running
    `ES_PATH_CONF=config.development ./bin/elasticsearch-service.bat install elasticsearch-development`
    `./bin/elasticsearch-service.bat start elasticsearch-development`
    and
    `ES_PATH_CONF=config.test ./bin/elasticsearch-service.bat install elasticsearch-test`
    `./bin/elasticsearch-service.bat start elasticsearch-test`
  - Unfortunately sometimes a service crashes, then you neet to run both commands again

# Install dependencies
- Run: `poetry install`

# Setup database
- Install constraints for neo4j for development and testing database (adapt the urls if you have a different setup):
  - Run: `poetry run neomodel_install_labels application application.models --db bolt://:@localhost:7687`
  - Run: `poetry run neomodel_install_labels application application.models --db bolt://:@localhost:17687`
 
# Download Wordkit for synonyms
- Run: `poetry run shovel utils.download_wordkit`

# Running tests
- Run: `poetry run mamba specs`

# Running linter
- Run: `poetry run black --check .`
- Run: `poetry run flake8 ./`

# Running auto-formater
- Run: `poetry run black .`

Autoformating and linting can be automized if you have [Pre-Commit](https://pre-commit.com/) installed on user.

# Start service
- Run: `poetry run flask run`

## Docu

You can find further documentation in the [wiki](https://github.com/hpi-sam/ask-your-repository-api/wiki).
