#!/bin/bash

source /opt/vc/.env

echo "Taking dump from $DB_HOST - hit any key to continue, or CTRL+C to cancel"
read

mv backup.sql backup.sql.bak

PGPASSWORD=$DB_PASS pg_dump --user=$DB_USER --host=$DB_HOST --port=$DB_PORT $DB_NAME > backup.sql
