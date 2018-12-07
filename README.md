# Elija &middot; [![Coverage Status](https://coveralls.io/repos/github/hpi-sam/ask-your-repository-api/badge.svg)](https://coveralls.io/github/hpi-sam/ask-your-repository-api)

# Setup service
- Install Python 3.7
- On Windows:
  - Click: Add path
  - At the end of installation allow usage of paths longer than 260 characters
  - See: [Setup Python](https://docs.python.org/3/using/windows.html)

- Setup Pipenv and flask:
  - [Install Pipenv](https://pipenv.readthedocs.io/en/latest/)
  - In project folder run `pipenv install`

- Copy .env.example into new .env file

- Install Elasticsearch
  - [Setup Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
  - Don't forget to set JAVA_HOME path to the path of java jdk

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
- Run: `pipenv install`
- And run: `pipenv install --dev`

# Setup database
- Run: `pipenv run python utils/setup_elasticsearch.py`

# Running tests
- Run: `pipenv run mamba specs`

# Running linter
- Run: `pipenv run pylint application/ specs/`

# Start service
- Run: `pipenv run flask run`
