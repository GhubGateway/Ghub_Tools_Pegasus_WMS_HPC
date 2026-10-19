#!/bin/bash -l

#--------------------------------------------------------------------------------
# MATLAB_Launch.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: a SLURM script
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# Echo to stdout:
echo "MATLAB_Launch.sh: $@"

start=$(date +%s)

module load ccrsoft/2023.01
module load matlab/2021b

# Avoid contention accessing /user/ghub/.mcrCache*
export MCR_CACHE_ROOT=${PWD}/mcrCache
echo ${MCR_CACHE_ROOT}

MCRROOT=/cvmfs/soft.ccr.buffalo.edu/versions/2023.01/easybuild/software/Core/matlab/2021b
LD_LIBRARY_PATH=.:${MCRROOT}/runtime/glnxa64;
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/bin/glnxa64;
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/sys/os/glnxa64;
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${MCRROOT}/sys/opengl/lib/glnxa64;
export LD_LIBRARY_PATH
echo LD_LIBRARY_PATH is ${LD_LIBRARY_PATH}

eval "$@"

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

:
