#!/bin/bash

if [[ -z "$@" ]]; then
    echo "Usage: $0 <prompt>"
    exit
fi

source venv/bin/activate
slug=$(echo "$@" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9][^a-z0-9]*/-/g')

if [[ -f "results/$slug.png" ]]; then
    echo "results/$slug.png exists - skipping"
    exit
fi

python3 generate.py -p "$@" -s 400 400
mv output.png results/$slug.png
