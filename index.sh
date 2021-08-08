#!/bin/bash

function doit () {
  rsync -a vc:/opt/vc/results/ results/

  echo "window.imagePaths = ["  > images.js

  for i in $(ls -1t results/*.{png,mp4}); do
    echo "'$i'," >> images.js
  done

  echo "];window.handler.drawImages();" >> images.js

  echo "index.sh: last pull:" $(date)
}

if [[ -z "$1" ]]; then
  doit
else
  while true; do
      doit
      sleep 150
      clear
  done
fi
