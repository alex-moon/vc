#!/bin/bash

if [[ -z "$@" ]]; then
    echo "Usage: $0 <prompt>"
    exit
fi

source venv/bin/activate
python3 vqgan_clip/generate.py -p "$@" -s 720 720 --video
slug=$(echo "$@" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9][^a-z0-9]*/-/g')
mv output.mp4 results/$slug.mp4
mv steps/500.png results/$slug.png

