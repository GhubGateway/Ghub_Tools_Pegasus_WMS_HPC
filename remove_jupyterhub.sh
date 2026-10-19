#!/bin/bash -l

echo "Removing  the jupyterhub container and cleaning the container cache..."
docker stop jupyterhub
docker rm jupyterhub
docker container prune -f

echo "Removing the jupyterhub-user-jovyan volume and cleaning the volume cache..."
docker volume rm jupyterhub-user-jovyan -f
docker volume prune -f

echo "Removing the jupyterhub image and cleaning the image cache..."
docker images --format "{{.Repository}}:{{.Tag}}" | grep "jupyterhub" | xargs -r docker rmi -f
#docker image prune -f

echo "Cleaning the build cache..."
#docker builder prune -f
