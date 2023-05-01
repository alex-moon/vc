#!/bin/bash

npm install
npx webpack build --node-env=public
ssh vos "
cp /opt/vc/public/assets/latest.json /opt/vc/latest.bak
"
rsync -av --delete public/ vos:/opt/vc/public/
ssh vos "
cd /opt/vc/
python3 latest.py
"
