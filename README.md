# Setup service
- Install Python 3.7
- On Windows:
  - Click: Add path
  - At the end of installation allow usage of paths longer than 260 characters
  - See: [Setup Python](https://docs.python.org/3/using/windows.html)
- Setup Flask:
  - In project folder run `py -m venv venv`
  - Run: `venv\Scripts\activate`
  - Add: *path-to-your-project*/venv/Scripts to your path variables
  - [Setup Flask](http://flask.pocoo.org/docs/1.0/installation/)
- Install Elasticsearch
  - [Setup Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
  - Don't forget to set JAVA_HOME path to the path of java jdk if you're using the service

# Install dependencies  
- Run: `pip install -r requirements.txt`

# Running tests
- Run: `python -m pytest -v tests`

# Start service
- Run: `flask run`
