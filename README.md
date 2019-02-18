# Elija &middot; [![Coverage Status](https://coveralls.io/repos/github/hpi-sam/ask-your-repository-api/badge.svg)](https://coveralls.io/github/hpi-sam/ask-your-repository-api)

# Setup service
- Install Python 3.7
- On Windows:
  - Click: Add path
  - At the end of installation allow usage of paths longer than 260 characters
  - See: [Setup Python](https://docs.python.org/3/using/windows.html)
- Highly recommended to use [pyenv](https://github.com/pyenv/pyenv#installation) instead for this as it makes swapping python versions much easier.  
You can use the installer from [here](https://github.com/pyenv/pyenv-installer) for easy installation.

Installing dependencies:
- **Setup Poetry**:
  - [Install Poetry](https://poetry.eustace.io/docs/#system-requirements)
  - Install dependencies via: `poetry install`
  
- If you don't have poetry installed yet but have pipenv installeed, you can try to use pipenv instead:  
  - In project folder run `pipenv install`
  - We don't regulary update our Pipfile anymore though so you might run into trouble!

- Copy .env.example into new .env file
- It's highly recommended you have docker installed it makes environment setup much easier: https://www.docker.com/get-started
- Install Neo4j
  - Neo4J is our GraphDB you can find more info and an install guide on it here: https://neo4j.com/
  - To run tests you need a neo4j installation on the ports specified in .env.testing
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
- Run: `poetry run shovel utils.setup_indices`

# Running tests
- Run: `poetry run mamba specs`

# Running linter
- Run: `poetry run prospector`

# Start service
- Run: `poetry run flask run`
