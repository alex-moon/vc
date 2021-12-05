#!/bin/bash

pass=$(cat /opt/vc/.env | grep SQLALCHEMY_DATABASE_URI | awk -F':' '{ print $3 }' | awk -F'@' '{ print $1 }')
host=$(cat /opt/vc/.env | grep SQLALCHEMY_DATABASE_URI | awk -F'@' '{ print $2 }' | awk -F':' '{ print $1 }')

echo "Taking dump from $host - hit any key to continue, or CTRL+C to cancel"
read

mv backup.sql backup.sql.bak
PGPASSWORD=$pass pg_dump --user=vc --host=$host vc > backup.sql
