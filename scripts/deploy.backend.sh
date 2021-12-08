#!/bin/bash

ssh vc "
cd /opt/vc
source venv/bin/activate

git pull origin \$(git rev-parse --abbrev-ref HEAD)

pip3 install -r requirements.api.txt

make migrate
"
