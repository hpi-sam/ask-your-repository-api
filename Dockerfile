FROM alpine:3.5
RUN apk add --update python py-pip
COPY requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
COPY application /src/application
COPY app.py /src/app.py
ENTRYPOINT ["python", "/src/app.py"]
