#!/bin/bash -l
tool_alias_name=$1
echo "removing "${tool_alias_name}"..."

rm -rf ./tools/${tool_alias_name}
rm -f ./containers/${tool_alias_name}/Dockerfile.hub
rm -f ./containers/${tool_alias_name}/docker-compose.yml
rm -rf ./containers/${tool_alias_name}/jupyterhub-data

docker stop jupyterhub
docker rm jupyterhub

docker volume rm jupyterhub-user-jovyan -f

[ -n "$(docker images -q ${tool_alias_name}-jupyterhub:latest)" ] && docker rmi ${tool_alias_name}-jupyterhub:latest
[ -n "$(docker images -q ${tool_alias_name}_tool_image:latest)" ] && docker rmi ${tool_alias_name}_tool_image:latest
[ -n "$(docker images -q quay.io/rljredhat/ghub_${tool_alias_name}_tool_image:tag)" ] && docker rmi quay.io/rljredhat/ghub_${tool_alias_name}_tool_image:tag

docker container prune -f
docker volume prune -f
docker builder prune -f
