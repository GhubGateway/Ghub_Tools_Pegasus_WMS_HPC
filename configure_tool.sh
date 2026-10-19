#!/bin/bash
tool_alias_name=$1

# Get to a known state
source ./unconfigure_tool.sh ${tool_alias_name}

# Configure ssh key pair credentials.
#The no-passcode setting copies over if you place the existing private and public key files into the correct folder inside your JupyterHub environment, because SSH keys store their passcode configuration inside the key files themselves.

# Inputs:
# ~/.ssh/id_ed2519

if ! [ -f ~/.ssh/id_ed25519 ]; then
    echo "~/.ssh/id_ed25519 is required to run this script."; return 2
fi

if ! [ -f ~/.ssh/id_ed25519.pub ]; then
    echo "~/.ssh/id_ed25519.pub is required to run this script."; return 2
fi

cp -f ~/.ssh/id_ed25519 ./submithost/.ssh/id_ed25519
cp -f ~/.ssh/id_ed25519.pub ./submithost/.ssh/id_ed25519.pub

vortex_host=vortex.ccr.buffalo.edu
echo "vortex_host: "${vortex_host}
vortex_user=$(awk '{print $NF}' ./submithost/.ssh/id_ed25519.pub | cut -d'@' -f1)
echo "vortex_user: "${vortex_user}

sed -i '' "s|VORTEX_HOST|${vortex_host}|g" ./submithost/Dockerfile.ghubex1
sed -i '' "s|VORTEX_USER|${vortex_user}|g" ./submithost/Dockerfile.ghubex1

sed -i '' "s|VORTEX_HOST|${vortex_host}|g" ./submithost/.ssh/config
sed -i '' "s|VORTEX_USER|${vortex_user}|g" ./submithost/.ssh/config

sed -i '' "s|VORTEX_HOST|${vortex_host}|g" ./tools/ghubex1/bin/launch_wrapper.py
sed -i '' "s|VORTEX_USER|${vortex_user}|g" ./tools/ghubex1/bin/launch_wrapper.py

:


