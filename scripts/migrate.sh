#!/bin/bash

sudo service supervisor stop
export FLASK_APP=vc.app:app
flask db migrate
flask db upgrade
sudo service supervisor start
