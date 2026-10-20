#!/bin/bash
tool_alias_name=$1

rm -f ./build.log
rm -f ./anaconda/Miniconda3-py310_25.11.1-1-Linux-x86_64.sh
rm -f ./submithost/.ssh/id_ed25519
rm -f ./submithost/.ssh/id_ed25519.pub

cp -f ./submithost/Dockerfile_template.ghubex1 ./submithost/Dockerfile.ghubex1
cp -f ./submithost/.ssh/config_template ./submithost/.ssh/config
cp -f ./tools/ghubex1/bin/launch_wrapper_template.py ./tools/ghubex1/bin/launch_wrapper.py

if [ -d "./submithost/LOCAL/shared-storage" ] && [ -n "$(ls -A ./submithost/LOCAL/shared-storage)" ]; then
    rm -rf ./submithost/LOCAL/shared-storage/*
    rm -rf ./submithost/LOCAL/shared-storage/.ipynb_checkpoints
fi

:
