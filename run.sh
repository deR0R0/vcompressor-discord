#!/bin/bash

# virtual environment
source ./virenv/bin/activate

# start gunicorn server
# change port and host as needed
gunicorn --bind 0.0.0.0:16061 --workers 4 src.webserver.app:app &

# start bot
python3 ./src/main.py