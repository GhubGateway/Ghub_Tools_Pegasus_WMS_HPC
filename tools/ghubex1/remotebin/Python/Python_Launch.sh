#!/bin/bash -l

#--------------------------------------------------------------------------------
# Python_Launch.sh
#--------------------------------------------------------------------------------

# Echo to stdout:
echo "Python_Launch.sh: $@"

start=$(date +%s)

module load ccrsoft/2023.01
module load gcccore/11.2.0
module load python/3.9.6

python "$@"

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

# Success status (exit code 0)
:
