#!/bin/bash

ssh vc "
cd /opt/vc
source venv/bin/activate

git pull origin \$(git rev-parse --abbrev-ref HEAD)

sudo service supervisor stop
FLASK_APP=vc.app:app
flask db migrate
flask db upgrade
sudo service supervisor start

npm install
npx webpack
"
