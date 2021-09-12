#!/bin/bash

source venv/bin/activate
sudo service supervisor stop
python3 -m vc.restore
sudo service supervisor start
