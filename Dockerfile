FROM python:3.7-alpine

RUN pip install pipenv

COPY . /src
WORKDIR /src

RUN pipenv install --system --deploy

EXPOSE 5000

CMD [ "flask", "run" ]
