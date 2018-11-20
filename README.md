# Elija

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

# Setup database
- Run: `pipenv run python utils/setup_elasticsearch.py`

# Running tests
- Run: `pipenv run python -m pytest -v tests` for testing without elasticsearch
- Run: `pipenv run python -m pytest -v tests --use-db` for testing with elasticsearch
- All calls to elasticsearch must by mocked **but** all elasticsearch queries must be tested in test_elasticsearch.py

# Start service
- Run: `pipenv run flask run`
