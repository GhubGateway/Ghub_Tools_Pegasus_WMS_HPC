#!/bin/bash
#
# sshslurm_common.sh -- sourced by the slurm_*.sh scripts of the
# "Slurm over plain ssh/scp" blahp instance.
#
# blahpd runs LOCALLY on the submit host (grid_resource = batch slurm, no
# user@host), so HTCondor's gridmanager never starts condor_ft-gahp and no
# ssh port forwarding is needed. Every interaction with the cluster is a
# plain `ssh <host> <command>` or `scp`, using the IDM-provisioned key.
#
# Settings (put them in the private blah.config written by install.sh):
#   sshslurm_host         user@vortex.ccr.buffalo.edu        (required)
#   sshslurm_key          ~/.ssh/id_ed25519                  (optional)
#   sshslurm_remote_base  absolute dir on the cluster for job dirs
#                         (default: $HOME/.blahp_ssh on the remote side)
#   sshslurm_multiplex    yes|no  reuse one ssh connection (ControlMaster)
#   sshslurm_cleanup      yes|no  delete the remote job dir after outputs
#                                 are fetched (default yes)
#   sshslurm_ssh_opts     extra ssh/scp -o options, space separated
#

: "${sshslurm_host:?sshslurm_host (user@host) must be set in blah.config}"

SSH_BIN=${SSH_BIN:-ssh}
SCP_BIN=${SCP_BIN:-scp}
sshslurm_state_dir=${sshslurm_state_dir:-$HOME/.blah/sshslurm_jobs}
mkdir -p "$sshslurm_state_dir"

sshslurm_opts=(-o BatchMode=yes -o ConnectTimeout=30 -o ServerAliveInterval=30
               -o StrictHostKeyChecking=accept-new)
if [ -n "$sshslurm_key" ]; then
    sshslurm_opts+=(-i "${sshslurm_key/#\~/$HOME}" -o IdentitiesOnly=yes)
fi
if [ "${sshslurm_multiplex:-yes}" = "yes" ]; then
    # Connection sharing is NOT port forwarding; it works with
    # AllowTcpForwarding=no. Set sshslurm_multiplex=no if the site blocks it.
    mkdir -p "$HOME/.ssh/cm" && chmod 700 "$HOME/.ssh/cm"
    sshslurm_opts+=(-o ControlMaster=auto -o "ControlPath=$HOME/.ssh/cm/%C"
                    -o ControlPersist=15m)
fi
for o in $sshslurm_ssh_opts; do sshslurm_opts+=(-o "$o"); done

# rssh <remote command string>
rssh() { "$SSH_BIN" "${sshslurm_opts[@]}" "$sshslurm_host" "$@"; }

# rbash [args...] < script   -- run a script from stdin in a remote login
# shell (so module/PATH setup that puts sbatch/squeue on PATH is loaded).
rbash() {
    local q="" a
    for a in "$@"; do q+=" $(printf '%q' "$a")"; done
    rssh "bash -l -s --$q"
}

# rscp_up <remote_dir> <local file|dir>...
rscp_up() {
    local dest=$1; shift
    [ $# -eq 0 ] && return 0
    "$SCP_BIN" -q -p -r "${sshslurm_opts[@]}" "$@" "$sshslurm_host:$dest/"
}

# rscp_down <remote file> <local file>
rscp_down() {
    "$SCP_BIN" -q -p "${sshslurm_opts[@]}" "$sshslurm_host:$1" "$2"
}

# Absolute remote base directory (cached after the first lookup).
sshslurm_remote_base_abs() {
    local base=${sshslurm_remote_base:-.blahp_ssh}
    if [ "${base:0:1}" != "/" ]; then
        local cache="$sshslurm_state_dir/.remote_home"
        if [ ! -s "$cache" ]; then
            rssh 'echo $HOME' > "$cache.tmp" 2>/dev/null && mv "$cache.tmp" "$cache"
        fi
        local rhome
        rhome=$(head -1 "$cache" 2>/dev/null)
        [ -z "$rhome" ] && return 1
        base="$rhome/$base"
    fi
    echo "$base"
}

# Make a path absolute against the job's (local) Iwd.
sshslurm_local_path() {
    if [ "${1:0:1}" = "/" ]; then echo "$1"; else echo "${bls_opt_workdir}/$1"; fi
}

# blahp job id "slurm/YYYYMMDD/12345" -> state file path
sshslurm_state_file() {
    local id=${1#slurm/}
    echo "$sshslurm_state_dir/${id//\//_}"
}
