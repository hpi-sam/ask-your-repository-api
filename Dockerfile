FROM python:3.7-alpine

WORKDIR /src

RUN apk add libffi-dev build-base tzdata

# pillow dependencies
RUN apk add jpeg-dev zlib-dev

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install poetry

RUN poetry config settings.virtualenvs.create false
RUN poetry install --no-dev

# text processing resources
RUN python -c "import nltk; nltk.download('all')"

COPY . .

EXPOSE 5000

CMD [ "./start-gunicorn.sh" ]
