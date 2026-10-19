#!/bin/bash -l

#--------------------------------------------------------------------------------
# Python_Launch.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: a SLURM script
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------

# Echo to stdout:
echo "Python_Launch.sh: $@"

commandError=0
ERROR_EXIT_CODE=1

# Ghub legacy check: Verify the python files do not contain unallowed system calls
pyFiles=$(ls *.py 2> /dev/null)
#echo ${pyFiles}
for pyFile in ${pyFiles} ; do
   echo "Verifying pyFile: ${pyFile}"
   for command in system popen subprocess ; do
      commandCount=$(grep -c -E "${command}[[:space:]]*\(|${command}[[:space:]]*\.\.\." ${pyFile})
      if [ ${commandCount} -gt 0 ] ; then
         echo "The Python command ${command} is not allowed in file ${pyFile}"
         commandError=1
      fi
   done
done

if [ ${commandError} -eq 1 ] ; then
   exit ${ERROR_EXIT_CODE}
fi

start=$(date +%s)

module load ccrsoft/2023.01
module load gcccore/11.2.0
module load python/3.9.6

python "$@"

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

:
