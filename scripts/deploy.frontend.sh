#!/bin/bash

ssh vc "
cd /opt/vc

git pull origin \$(git rev-parse --abbrev-ref HEAD)

npm install
npx webpack build --node-env=private
"
