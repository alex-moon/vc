#!/bin/bash

cmd=$1
if [[ -z "$cmd" ]]; then
    cmd=image
fi

IFS=$'\n'
for test in $(cat tests.txt); do
    ./$cmd.sh "$test"
    for style in $(cat styles.txt); do
	if [[ -z "$style" ]]; then
	    break
        fi
        ./$cmd.sh "$test | $style"
    done
done

