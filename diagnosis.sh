#!/bin/bash

while true; do
  echo 'Diagnostics as at ' $(date)
  echo 'top'
  top -bn1 -o +%MEM | head -n10
  echo
  echo 'db'
  ./db.sh -c "
    SELECT id, started, completed, failed, steps_completed, steps_total
    FROM generation_request WHERE id = (SELECT MAX(id) FROM generation_request)
  "
  echo 'logs'
  tail -n1000 log/vc.* | grep DIAG
  sleep 10
  clear
done
