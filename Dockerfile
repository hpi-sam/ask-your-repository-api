FROM python:3.7-alpine

RUN apk add libffi-dev build-base

# pillow dependencies
RUN apk add jpeg-dev zlib-dev

RUN pip install poetry

COPY . /src
WORKDIR /src
RUN poetry config settings.virtualenvs.create false
RUN poetry install --no-dev

# text processing resources
RUN poetry run python -c "import nltk; nltk.download('all')"

EXPOSE 5000

CMD [ "./start-gunicorn.sh" ]
