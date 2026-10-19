#!/bin/bash
# slurm_ping.sh -- "Slurm over ssh" blahp: can we ssh in and reach Slurm?
. `dirname $0`/blah_load_config.sh
. `dirname $0`/sshslurm_common.sh
out=$(rssh "bash -l -c 'squeue -h -u \$USER -o %i >/dev/null'" 2>&1)
if [ $? -eq 0 ]; then
    echo "0 No error"
else
    echo "1 ssh/squeue error on $sshslurm_host: $(echo $out)"
fi
exit 0
