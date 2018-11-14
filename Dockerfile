FROM python:3.7-alpine

RUN pip install pipenv

COPY . /src
WORKDIR /src

RUN pipenv install

ENTRYPOINT ["python"]
CMD ["-m", "/src/app.py"]
