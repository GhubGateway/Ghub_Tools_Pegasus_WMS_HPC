#!/bin/bash
# slurm_hold.sh -- "Slurm over ssh" blahp: scontrol hold over ssh.
. `dirname $0`/blah_load_config.sh
. `dirname $0`/sshslurm_common.sh
jobid=${1##*/}; M=""
[[ $jobid == *@* ]] && M="-M ${jobid#*@}"
jobid=${jobid%%@*}
if rssh "bash -l -c 'scontrol $M hold $jobid || scontrol $M requeuehold $jobid'" >/dev/null 2>&1; then
    echo " 0 No\\ error"; exit 0
fi
echo " 1 Error"; exit 1
