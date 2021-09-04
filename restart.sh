#!/bin/bash

git pull origin $(git rev-parse --abbrev-ref HEAD)
sudo service supervisor restart
tail -f /var/log/supervisor/*worker*
