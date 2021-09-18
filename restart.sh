#!/bin/bash

git pull origin $(git rev-parse --abbrev-ref HEAD)
if [[ ! -z "$1" ]]; then
  ./restore.sh
else
  sudo service supervisor restart
fi
npx webpack
tail -f /var/log/supervisor/* /opt/vc/log/*
