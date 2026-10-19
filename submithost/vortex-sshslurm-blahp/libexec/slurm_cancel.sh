#!/bin/bash
# slurm_cancel.sh -- "Slurm over ssh" blahp: scancel over ssh.
. `dirname $0`/blah_load_config.sh
. `dirname $0`/sshslurm_common.sh

jnr=$#; jc=0
for job in "$@"; do
    jobid=${job##*/}; M=""
    [[ $jobid == *@* ]] && M="-M ${jobid#*@}"
    jobid=${jobid%%@*}
    cmdout=$(rssh "bash -l -c 'scancel $M $jobid'" 2>&1)
    retcode=$?
    # already gone == cancelled
    echo "$cmdout" | grep -qi 'Invalid job id' && retcode=0
    if [ "$retcode" == "0" ]; then msg=" 0 No\\ error"
    else msg=" $retcode $(echo $cmdout | sed 's/ /\\ /g')"; fi
    if [ "$jnr" == "1" ]; then echo "$msg"; else echo ".$jc$msg"; fi
    jc=$((jc+1))
done
exit 0
