#!/bin/bash
#
# slurm_status.sh -- "Slurm over plain ssh/scp" blahp status script.
#   slurm_status.sh [-w] [-n] slurm/<date>/<jobid> [...]
# Prints one line per job:  0[BatchJobId="<id>";JobStatus=<n>;ExitCode=<rc>;]
#   JobStatus: 1 idle, 2 running, 3 removed, 4 completed, 5 held
# When a job is finished, stdout/stderr/output files are scp'd back to the
# submit host BEFORE status 4 is reported, so HTCondor/Pegasus see them.

. `dirname $0`/blah_load_config.sh
. `dirname $0`/sshslurm_common.sh

while getopts "wn" arg; do
    case "$arg" in
        w) ;;
        n) echo "$sshslurm_host"; exit 0 ;;
        *) echo "Usage: $0 [-w] [-n] slurm/<date>/<jobid> ..."; exit 1 ;;
    esac
done
shift $((OPTIND - 1))

# Remote probe, one ssh per job:
#   STATE <squeue state> | DONE <rc> | SACCT <State>|<ExitCode> | UNKNOWN
read -r -d '' probe <<'EOF'
id=$1; dir=$2; M=${3:+-M $3}
st=$(squeue $M -h -j "$id" -o %T 2>/dev/null | grep -v '^CLUSTER' | head -1)
if [ -n "$st" ]; then echo "STATE $st"; exit 0; fi
if [ -f "$dir/.blahp_exitcode" ]; then echo "DONE $(cat "$dir/.blahp_exitcode")"; exit 0; fi
sa=$(sacct $M -n -P -X -j "$id" -o State,ExitCode 2>/dev/null | head -1)
if [ -n "$sa" ]; then echo "SACCT $sa"; else echo "UNKNOWN"; fi
EOF

fetch_outputs() {   # $1 = state file
    local ok=0 type rest localf remotef
    while IFS= read -r line; do
        type=${line%%::*}; rest=${line#*::}
        [ "$type" = "remote_dir" ] && continue
        localf=${rest%%:*}; remotef=${rest#*:}
        mkdir -p "$(dirname "$localf")"
        case "$type" in
            stdout|stderr|output)
                rscp_down "$remotef" "$localf" || { [ "$type" = output ] && ok=1; } ;;
            append)
                rscp_down "$remotef" "$localf.blahp_err" && cat "$localf.blahp_err" >> "$localf"
                rm -f "$localf.blahp_err" ;;
        esac
    done < "$1"
    return $ok
}

for reqfull in "$@"; do
    jobid=${reqfull##*/}; cluster=""
    [[ $jobid == *@* ]] && cluster=${jobid#*@}
    jobid=${jobid%%@*}
    state_file=$(sshslurm_state_file "$reqfull")
    remote_dir=""
    [ -r "$state_file" ] && remote_dir=$(grep '^remote_dir::' "$state_file" | head -1 | cut -d: -f3-)

    out=$(rbash "$jobid" "${remote_dir:-/nonexistent}" $cluster <<< "$probe" 2>&1)
    if [ $? -ne 0 ]; then
        echo "1Error: ssh status query failed: $(echo $out)"
        continue
    fi
    line=$(echo "$out" | grep -E '^(STATE|DONE|SACCT|UNKNOWN)' | tail -1)
    kind=${line%% *}; val=${line#* }
    status=""; exitcode=""
    case "$kind" in
        STATE)
            case "$val" in
                PENDING|CONFIGURING|REQUEUED|REQUEUE_FED|RESV_DEL_HOLD) status=1 ;;
                RUNNING|COMPLETING|SUSPENDED|STOPPED|SIGNALING|STAGE_OUT|RESIZING) status=2 ;;
                REQUEUE_HOLD|SPECIAL_EXIT) status=5 ;;
                CANCELLED*) status=3 ;;
                *) status=2 ;;   # COMPLETED/FAILED still in squeue: wait for exit file
            esac ;;
        DONE)
            status=4; exitcode=${val//[^0-9]/}; exitcode=${exitcode:-1} ;;
        SACCT)
            st=${val%%|*}; ec=${val#*|}
            case "$st" in
                PENDING*) status=1 ;;
                RUNNING*|COMPLETING*) status=2 ;;
                CANCELLED*) status=3 ;;
                *) status=4; exitcode=${ec%%:*}
                   [ "$st" != "COMPLETED" ] && [ "${exitcode:-0}" = "0" ] && exitcode=1 ;;
            esac ;;
        *)
            # Not in squeue, no exit-code file, no accounting: allow a few
            # polls for filesystem lag before declaring failure.
            n=$(( $(cat "$state_file.unknown" 2>/dev/null || echo 0) + 1 ))
            echo $n > "$state_file.unknown"
            if [ $n -ge 3 ]; then status=4; exitcode=1; else status=2; fi ;;
    esac

    if [ "$status" = "4" ] || [ "$status" = "3" ]; then
        if [ -r "$state_file" ]; then
            if ! fetch_outputs "$state_file"; then
                echo "1Error: job $jobid finished but fetching outputs from $sshslurm_host failed"
                continue
            fi
            if [ "${sshslurm_cleanup:-yes}" = "yes" ] && [ -n "$remote_dir" ]; then
                rssh "rm -rf '$remote_dir'" >/dev/null 2>&1
            fi
            rm -f "$state_file" "$state_file.unknown"
        fi
    fi

    result="[BatchJobId=\"$jobid\";JobStatus=$status;"
    [ -n "$exitcode" ] && result="${result}ExitCode=$exitcode;"
    echo "0${result}]"
done
exit 0
