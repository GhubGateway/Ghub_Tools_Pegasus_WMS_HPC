#!/bin/bash -l
tool_alias_name=$1
echo "launching "${tool_alias_name}"..."

source ./remove_jupyterhub.sh

cp -f ./jupyterhub/Dockerfile.hub ./submithost
cp -f ./jupyterhub/docker-compose.yml ./submithost

(cd ./submithost && docker compose up --build)
