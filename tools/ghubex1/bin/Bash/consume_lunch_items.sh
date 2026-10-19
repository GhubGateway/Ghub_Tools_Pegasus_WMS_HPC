# !/bin/bash -l

#--------------------------------------------------------------------------------
# consume_lunch_items.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: Bash_Launch.sh
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# In the Pegasus WMS YAML file,
# this job is specified to have the f.b input file and the f.c output file

# f.b contains the served lunch items

echo -e "`cat f.b` Thank you for lunch. Yum Yum!!" > f.c

# f.c contains the thank you note
