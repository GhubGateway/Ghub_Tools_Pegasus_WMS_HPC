#!/bin/bash -l

# When low on disk space,
# clean up, clean up, everybody do their share...
echo "Removing tool images and cleaning the image cache......"
docker images --format "{{.Repository}}:{{.Tag}}" | grep "tool_image" | xargs -r docker rmi -f
docker image prune -f

echo "Cleaning the build cache..."
docker builder prune -f

docker images -a
