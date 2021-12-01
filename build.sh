#!/bin/bash

sudo apt update
sudo apt install -y python3-pip python3-venv ffmpeg zip wget curl jq postgresql ca-certificates redis-server redis-tools supervisor nginx
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ 'lsb_release -cs'-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo snap install node --classic
sudo npm install -g npm
sudo npm install -g npx
sudo npm install -g n
sudo n v16.13.0
npm install

./build.api.sh
if [[ ! -z "$(grep 'ROLE=.*worker' .env)" ]]; then
  ./build.worker.sh
fi

sudo -u postgres createuser -d vc -P
sudo -u postgres createdb -O vc vc
