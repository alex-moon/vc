#!/bin/bash

mode=$1
if [[ -z "$mode" ]]; then
    mode=images
fi

IFS=$'\n'
LR=0.1
OPTIMISER=Adam
MAX_ITERATIONS=25
SEED=`shuf -i 1-9999999999 -n 1`
FILENAME=input.png
FILENAME_NO_EXT=input
FILE_EXTENSION=png

function images() {
    ./image.sh "$@"
}

function zoom() {
    python3 generate.py -p="$@" -opt="$OPTIMISER" -lr=$LR -i=$MAX_ITERATIONS -se=$MAX_ITERATIONS --seed=$SEED -o="$FILENAME"
    cp "$FILENAME" "$FILENAME_NO_EXT"-0000."$FILE_EXTENSION"
    convert "$FILENAME" -distort SRT 1.01,0 -gravity center "$FILENAME"	# Zoom
    convert "$FILENAME" -distort SRT 1 -gravity center "$FILENAME"	# Rotate
}

for test in $(cat tests.txt); do
    $mode "$test"
    for style in $(cat styles.txt); do
        if [[ -z "$style" ]]; then
            break
        fi
        $mode "$test | $style"
    done
done

if [[ "$mode" -eq "zoom" ]]; then
    ffmpeg -y -i "$FILENAME_NO_EXT"-%04d."$FILE_EXTENSION" -b:v 8M -c:v h264_nvenc -pix_fmt yuv420p -strict -2 -filter:v "minterpolate='mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=60'" video.mp4
fi
