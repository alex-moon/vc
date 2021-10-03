#!/bin/bash

npm install
npx webpack build --node-env=public
rsync -av --delete public/ vos:/opt/vc/public/
ssh vos "
cd /opt/vc/
python3 latest.py
"
