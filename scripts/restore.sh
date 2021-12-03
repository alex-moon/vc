#!/bin/bash

pass=$(cat /opt/vc/.env | grep SQLALCHEMY_DATABASE_URI | awk -F':' '{ print $3 }' | awk -F'@' '{ print $1 }')

alias dbp=PGPASSWORD=$pass psql --user=vc --host=vc-api.ajmoon.uk postgres
dbp "SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid <> pg_backend_pid()
AND datname = 'vc'"
dbp "DROP DATABASE vc'"
dbp "CREATE DATABASE vc WITH OWNER vc"

alias dbvc=PGPASSWORD=$pass psql --user=vc --host=vc-api.ajmoon.uk vc
dbvc < backup.sql
