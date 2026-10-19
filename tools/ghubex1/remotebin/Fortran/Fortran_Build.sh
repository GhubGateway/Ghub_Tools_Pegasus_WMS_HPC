#!/bin/bash -l

#--------------------------------------------------------------------------------
# Fortran_Build.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: a SLURM script
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# Echo to stdout:
echo "Fortran_Build.sh"

start=$(date +%s)

module load ccrsoft/2023.01
module load gcc/11.2.0

# gfortran creates Fortran executables to run on a platform corresponding to the platform on which they are generated.

gfortran=$(which gfortran)
echo 'gfortran: '${gfortran}

# -v: verbose
# -o: output file

${gfortran} -v ./receive_lunch_items.f90 -o receive_lunch_items
${gfortran} -v ./consume_lunch_items.f90 -o consume_lunch_items

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

:
