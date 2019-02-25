#!/bin/sh

gunicorn \
  --worker-class eventlet \
  --access-logfile - \
  --log-level info \
  -w 1 \
  -b :5000 \
  production:app
