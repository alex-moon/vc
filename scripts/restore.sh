#!/bin/bash

pass=$(cat /opt/vc/.env | grep SQLALCHEMY_DATABASE_URI | awk -F':' '{ print $3 }' | awk -F'@' '{ print $1 }')
host=$(cat /opt/vc/.env | grep SQLALCHEMY_DATABASE_URI | awk -F'@' '{ print $2 }' | awk -F':' '{ print $1 }')

set -x

dbp() {
  PGPASSWORD=$pass psql --user=vc --host=$host postgres -c "$@"
}
dbp "SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid <> pg_backend_pid()
AND datname = 'vc'"
dbp "DROP DATABASE vc"
dbp "CREATE DATABASE vc WITH OWNER vc"

PGPASSWORD=$pass psql --user=vc --host=$host vc < backup.sql
