#!/bin/bash

function dowrite () {
    echo "window.imagePaths = [";

    for i in `ls -1t results/*.{png,mp4}`; do
        echo "'$i',";
    done
    
    echo "];window.handler.drawImages();"
}

while true; do
    echo "index.sh: last pull:" $(date)
    rsync -a vc:/opt/vc/results/ results/
    dowrite > images.js
    sleep 150
    clear
done
