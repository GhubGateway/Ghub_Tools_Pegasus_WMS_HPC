#!/bin/bash -l
tool_alias_name=$1
echo "building submithost image for "${tool_alias_name}"..."

( cd ./anaconda && [ ! -f "Miniconda3-py310_25.11.1-1-Linux-x86_64.sh" ] && wget https://repo.anaconda.com/miniconda/Miniconda3-py310_25.11.1-1-Linux-x86_64.sh )

[ -n "$(docker images -q ${tool_alias_name}_tool_image:latest)" ] && docker rmi ${tool_alias_name}_tool_image:latest
docker image build -f ./submithost/Dockerfile.${tool_alias_name} -t ${tool_alias_name}_tool_image:latest . 2>&1 | tee build.log
