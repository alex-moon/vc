#!/bin/bash

git pull origin feature/VC-7-inpainting-service
sudo supervisorctl -c /etc/supervisor/supervisord.conf reload
tail -f data/log/*

