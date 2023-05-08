#!/bin/bash

python3 -m venv venv
source venv/bin/activate
export FLASK_ENV=development
export FLASK_APP="vc:create_app()"
flask run --host=0.0.0.0
