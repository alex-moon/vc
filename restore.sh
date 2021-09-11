#!/bin/bash

source venv/bin/activate
sudo supervisorctl stop all
python3 -m vc.restore
sudo supervisorctl start all
