#!/bin/bash

IFS=$'\n'
LR=0.1
OPTIMISER=Adam
MAX_ITERATIONS=300
MAX_EPOCHS=10
MAX_REPEATS=10
SEED=`shuf -i 1-9999999999 -n 1`

i=0
function generate() {
    padded_count=$(printf "%04d" "$i")
    python3 generate.py -p="$1" \
        -opt="$OPTIMISER" \
        -lr=$LR \
        -i=$MAX_ITERATIONS \
        -se=$MAX_ITERATIONS \
        --seed=$SEED \
        -ii="input/input.png" \
        -o="input/input.png"
    cp "input/input.png" "input/input-$padded_count.png"
    (( i ++ ))
}

function zoom() {
    for (( j=1; j<=$MAX_EPOCHS; j++ )); do
        generate "$1"

        # scale, rotate, translate: <coords from>, <scale (multiple)>, <rotate (degrees)>, <coords to>
        convert "input/input.png" -distort SRT "0,0 1.01 1 10,0" -gravity center "input/input.png"
    done
}

function zoom3d() {
    for (( j=1; j<=$MAX_EPOCHS; j++ )); do
        generate "$1"

        python3 zoom3d.py "input/input.png"
        mv results/input.png input/input.png
    done
}

for (( repeat=1; repeat<=$MAX_REPEATS; repeat++ )); do
for test in $(cat tests.txt); do
    zoom3d "$test"
    for style in $(cat styles.txt); do
        if [[ -z "$style" ]]; then
            break
        fi
        zoom3d "$test | $style"
    done
done
done

ffmpeg -y -i "input/input-%04d.png" -b:v 8M -c:v h264_nvenc -pix_fmt yuv420p -strict -2 -filter:v "minterpolate='mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=60'" results/video-$(date -Iseconds | sed 's/[^0-9]/-/g').mp4
