#!/bin/bash

source /opt/vc/.env

set -x

dbp() {
  PGPASSWORD=$DB_PASS psql --user=$DB_USER --host=$DB_HOST postgres -c "$@"
}
dbp "SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid <> pg_backend_pid()
AND datname = 'vc'"
dbp "DROP DATABASE vc"
dbp "CREATE DATABASE vc WITH OWNER vc"

PGPASSWORD=$DB_PASS psql --user=$DB_USER --host=$DB_HOST vc < backup.sql
