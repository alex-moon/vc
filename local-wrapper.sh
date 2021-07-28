#!/bin/bash

if [[ -z "$@" ]]; then
    echo "Usage: $0 <prompt>"
    exit
fi

source venv/bin/activate
python generate.py -p "$@"
