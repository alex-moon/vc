#!/bin/bash

pass=$(cat .env | grep SQLALCHEMY_DATABASE_URI | awk -F':' '{ print $3 }' | awk -F'@' '{ print $1 }')
PGPASSWORD=$pass psql --user=vc --host=127.0.0.1 vc "$@"

