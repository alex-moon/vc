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
if [[ -z "$(grep SALT .env)" ]]; then
  echo SALT=$(date | md5sum | base64 | head -c22) >> .env
fi
if [[ -z "$(grep SQLALCHEMY_DATABASE_URI .env)"]]; then
  echo "SQLALCHEMY_DATABASE_URI=postgresql://vc:$(uuid | base64 | head -c16)@127.0.0.1:5432/vc"
fi

pass=$(cat /opt/vc/.env | grep SQLALCHEMY_DATABASE_URI | awk -F':' '{ print $3 }' | awk -F'@' '{ print $1 }')
sudo -u postgres psql -c "CREATE USER vc WITH ENCRYPTED PASSWORD '$pass'"
sudo -u postgres createdb -O vc vc
