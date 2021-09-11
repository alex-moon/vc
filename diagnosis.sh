#!/bin/bash

while true; do
  echo 'Diagnostics as at ' $(date)
  echo 'top'
  top -bn1 -o +%MEM | head -n10 | tail -n4 |  awk '{ printf("%-8s  %-8s  %-8s\n", $9, $10, $12); }'
  echo
  echo 'db'
  ./db.sh -c "
    SELECT id, started, completed, failed, steps_completed, steps_total
    FROM generation_request WHERE id = (SELECT MAX(id) FROM generation_request)
  "
  echo 'logs'
  grep "DEBUG.*DEBUG" log/vc.* | tail -n10
  sleep 5
  clear
done
