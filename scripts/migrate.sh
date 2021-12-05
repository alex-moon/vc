#!/bin/bash

sudo service supervisor stop
source venv/bin/activate
export FLASK_APP=vc.app:app
flask db migrate
flask db upgrade
sudo service supervisor start
