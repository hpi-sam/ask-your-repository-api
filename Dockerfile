FROM python:3.7-alpine

RUN apk add build-base
RUN pip install pipenv

COPY . /src
WORKDIR /src

RUN pipenv install --system --deploy

EXPOSE 5000

CMD [ "gunicorn", "--worker-class", "eventlet", "--access-logfile", "-", "-w", "1", "-b", ":5000", "app:app" ]
