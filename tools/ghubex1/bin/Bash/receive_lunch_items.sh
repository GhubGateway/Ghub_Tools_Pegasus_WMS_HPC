# !/bin/bash -l

#--------------------------------------------------------------------------------
# receive_lunch_items.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: Bash_Launch.sh
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# In the Pegasus WMS YAML file,
# this job is specified to have the f.a input file and the f.b output file

username=${1}

# f.a contains the received lunch items

# Serve the lunch items
echo -e "Hello ${username}! Received lunch items: `cat f.a`." > f.b

# f.b contains the served lunch items
