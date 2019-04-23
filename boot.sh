#!/bin/sh -e

export SECRET_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
exec gunicorn -b 0.0.0.0:5000 -w 10 app:app

