#!/bin/bash -l

#--------------------------------------------------------------------------------
# R_Launch.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: a SLURM script
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# Echo to stdout:
echo "R_Launch.sh: $@"

start=$(date +%s)

module load ccrsoft/2023.01
module load gcc/11.2.0
module load openmpi/4.1.1
module load r/4.2.0

Rscript "$@"

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

:
