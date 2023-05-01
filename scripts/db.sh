#!/bin/bash

source /opt/vc/.env

echo "Connecting to $DB_HOST"

PGPASSWORD=$DB_PASS psql --user=$DB_USER --host=$DB_HOST --port=$DB_PORT $DB_NAME
