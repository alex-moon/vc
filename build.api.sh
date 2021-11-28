#!/bin/bash

if [[ ! -d "venv" ]]; then
  python3 -m venv venv
fi
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install --no-cache-dir wheel decorator
pip3 install --no-cache-dir -r requirements.api.txt

echo "Done [api]"
