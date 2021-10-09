#!/bin/bash

python3 -m venv venv
source venv/bin/activate
uwsgi --ini vc/uwsgi.ini
