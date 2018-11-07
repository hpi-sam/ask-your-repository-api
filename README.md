# Setup service
- Install python 3.7
- On Windows:
  - Click: Add path
  - At the end of installation allow usage of paths longer than 260 characters
  - See: [Setup Python](https://docs.python.org/3/using/windows.html)
- Setup flask:
  - In project folder run `py -m venv venv`
  - Run: `venv\Scripts\activate`
  - Add: *path-to-your-project*/venv/Scripts to your path variables
  - [Setup Flask](http://flask.pocoo.org/docs/1.0/installation/)

# Install dependencies  
- Run: `pip install -r requirements.txt`

# Running Tests
- Run: `python -m pytest -v tests`

# Start service
- Run: `flask run`
