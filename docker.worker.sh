#!/bin/bash

Xvfb :0 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
export DISPLAY=:0

python3 -m venv venv
source venv/bin/activate
python3 -m vc.worker
