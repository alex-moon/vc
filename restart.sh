#!/bin/bash

git pull origin $(git rev-parse --abbrev-ref HEAD)
sudo service supervisor stop
./restore.sh
sudo service supervisor start
tail -f /var/log/supervisor/* /opt/vc/log/*
