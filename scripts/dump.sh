#!/bin/bash

mv backup.sql backup.sql.bak
pass=$(cat /opt/vc/.env | grep SQLALCHEMY_DATABASE_URI | awk -F':' '{ print $3 }' | awk -F'@' '{ print $1 }')
PGPASSWORD=$pass pg_dump --user=vc --host=vc-api.ajmoon.uk vc > backup.sql
