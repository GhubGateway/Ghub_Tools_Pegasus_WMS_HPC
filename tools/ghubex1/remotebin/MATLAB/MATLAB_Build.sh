#!/bin/bash -l

#--------------------------------------------------------------------------------
# MATLAB_Build.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: a SLURM script
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# Echo to stdout:
echo "MATLAB_Build.sh"

start=$(date +%s)

module load ccrsoft/2023.01
module load matlab/2021b

# mcc creates MATLAB executables to run on a platform corresponding to the platform on which they are generated.

mcc=$(which mcc)
echo 'mcc: '${mcc}

# -m: generate a standalone application
# -v: verbose
# -o: output file

${mcc} -m -v ./receive_lunch_items.m -o receive_lunch_items
chmod 755 receive_lunch_items
${mcc} -m -v ./consume_lunch_items.m -o consume_lunch_items
chmod 755 consume_lunch_items

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

:
