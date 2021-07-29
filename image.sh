#!/bin/bash

if [[ -z "$@" ]]; then
    echo "Usage: $0 <prompt>"
    exit
fi

source venv/bin/activate
python3 generate.py -p "$@" -s 400 400
slug=$(echo "$@" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9][^a-z0-9]*/-/g')
mv output.png results/$slug.png

