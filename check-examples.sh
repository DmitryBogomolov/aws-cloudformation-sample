#!/bin/bash

cwd=$(pwd)
names=($(ls -d examples/*))
count=0

for name in "${names[@]}"; do
    cd "$name"
    ./run.py process
    exit_code=$?
    count=$(($count + $exit_code))
    cd "$cwd"
done

if [[ "$count" -ne 0 ]]; then
    exit 1
fi
