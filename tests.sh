#!/bin/bash

cmd=$0
if [[ -z "$cmd" ]]; then
    cmd=image
fi

IFS=$'\n'
for test in $(cat tests.txt); do
    ./$cmd.sh "$test"
    ./$cmd.sh "$test | unreal engine"
done

