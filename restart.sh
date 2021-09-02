#!/bin/bash

git pull origin $(git rev-parse --abbrev-ref HEAD)
sudo supervisorctl -c /etc/supervisor/supervisord.conf reload
tail -f data/log/*
