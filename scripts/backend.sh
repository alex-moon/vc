#!/bin/bash

docker exec -it $(docker ps | grep vc_flask | awk '{ print $1 }') bash -c "
source venv/bin/activate

pip3 install -r requirements.api.txt

scripts/migrate.sh
"
