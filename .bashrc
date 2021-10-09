#!/bin/bash

pyv () {
  python -m trace -t $1 | grep $1
}

venv() {
  python3 -m venv venv
  source venv/bin/activate
  # pip install -r requirements.txt
}

run() {
  export FLASK_ENV=development
  export FLASK_APP="vc:create_app()"
  flask run --host=0.0.0.0
}

venv

