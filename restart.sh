#!/bin/bash

git pull origin $(git rev-parse --abbrev-ref HEAD)
./restore.sh
tail -f /var/log/supervisor/* /opt/vc/log/*
