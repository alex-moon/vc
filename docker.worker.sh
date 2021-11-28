#!/bin/bash

if [[ -z "$(grep 'ROLE.*worker' .env)" ]]; then
  echo "Role is not worker, so not starting worker."
  sleep 999999999
  exit
fi

Xvfb :0 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
export DISPLAY=:0

python3 -m venv venv
source venv/bin/activate
python3 -m vc.worker
