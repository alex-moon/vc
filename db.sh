#!/bin/bash

# postgresql://vc:76c55c60f5ee61c99745b33df50e7f87@127.0.0.1:5432/vc

pass=$(cat .env | grep SQLALCHEMY_DATABASE_URI | awk -F':' '{ print $3 }' | awk -F'@' '{ print $1 }')
PGPASSWORD=$pass psql --user=vc --host=127.0.0.1 vc

