#!/bin/bash
#
# install.sh -- install a private "Slurm over plain ssh/scp" blahp on the
# submit host so that   grid_resource = batch slurm   (NO user@host)
# submits to a remote Slurm cluster without condor_ft-gahp and without
# ssh port forwarding.
#
# Why: for grid_resource = batch slurm user@host, HTCondor's gridmanager
# (infnbatchjob.cpp, 24.0 and main) ALWAYS starts condor_ft-gahp through
# remote_gahp with `ssh -R` and runs DOWNLOAD_SANDBOX before every submit.
# There is no knob to turn that off. With no user@host the blahp is local
# and the ft-gahp is never created; these scripts do the ssh/scp instead.
#
# Usage (run as the user that owns the condor_schedd / submits jobs; use
# sudo only for the --condor-config step if /etc/condor/config.d is root's):
#
#   ./install.sh --host jdoe@vortex.ccr.buffalo.edu \
#                --key ~/.ssh/id_ed25519 \
#                [--prefix ~/.blahp-sshslurm] \
#                [--remote-base /vscratch/grp-lab/jdoe/blahp_jobs] \
#                [--condor-config /etc/condor/config.d/60-vortex-sshslurm.config]
#
set -euo pipefail

HOST="" KEY="" PREFIX="$HOME/.blahp-sshslurm" REMOTE_BASE="" MULTIPLEX=yes
CONDOR_CFG=""
here=$(cd "$(dirname "$0")" && pwd)

while [ $# -gt 0 ]; do
    case "$1" in
        --host) HOST=$2; shift 2 ;;
        --key) KEY=$2; shift 2 ;;
        --prefix) PREFIX=$2; shift 2 ;;
        --remote-base) REMOTE_BASE=$2; shift 2 ;;
        --no-multiplex) MULTIPLEX=no; shift ;;
        --condor-config) CONDOR_CFG=$2; shift 2 ;;
        *) echo "unknown option $1" >&2; exit 2 ;;
    esac
done
[ -n "$HOST" ] || { echo "--host user@host is required" >&2; exit 2; }

# ---- locate the stock blahp that ships with HTCondor 24 -------------------
stock_blahpd=$(condor_config_val BATCH_GAHP 2>/dev/null || true)
[ -x "$stock_blahpd" ] || stock_blahpd=$(command -v blahpd || true)
for c in /usr/bin/blahpd /usr/sbin/blahpd /usr/libexec/blahp/blahpd; do
    [ -x "$stock_blahpd" ] && break; stock_blahpd=$c
done
[ -x "$stock_blahpd" ] || { echo "cannot find HTCondor's blahpd" >&2; exit 1; }

stock_libexec=""
for c in "$(condor_config_val GLITE_LOCATION 2>/dev/null || true)/libexec/blahp" \
         "$(condor_config_val GLITE_LOCATION 2>/dev/null || true)/libexec" \
         /usr/libexec/blahp; do
    [ -r "$c/blah_common_submit_functions.sh" ] && { stock_libexec=$c; break; }
done
[ -n "$stock_libexec" ] || { echo "cannot find blah_common_submit_functions.sh" >&2; exit 1; }

peg_attrs=""
for c in "$(dirname "$(command -v pegasus-plan)")/../share/pegasus/htcondor/glite" \
         /usr/share/pegasus/htcondor/glite; do
    [ -r "$c/slurm_local_submit_attributes.sh" ] && { peg_attrs=$c/slurm_local_submit_attributes.sh; break; }
done

echo "stock blahpd     : $stock_blahpd"
echo "stock blahp dir  : $stock_libexec"
echo "pegasus attrs    : ${peg_attrs:-NOT FOUND (pegasus resource profiles will be ignored)}"
echo "install prefix   : $PREFIX"

# ---- private libexec -------------------------------------------------------
mkdir -p "$PREFIX/libexec" "$PREFIX/bin"
cp "$stock_libexec/blah_common_submit_functions.sh" \
   "$stock_libexec/blah_load_config.sh" "$PREFIX/libexec/"
cp "$here"/libexec/*.sh "$PREFIX/libexec/"
# Pegasus maps cores/memory/runtime/queue/project/glite.arguments to #SBATCH
# lines through this file (sourced by bls_set_up_local_and_extra_args).
[ -n "$peg_attrs" ] && cp "$peg_attrs" "$PREFIX/libexec/slurm_local_submit_attributes.sh"
chmod +x "$PREFIX"/libexec/*.sh

# ---- private blah.config ---------------------------------------------------
cat > "$PREFIX/blah.config" <<EOF
# private blahp config: Slurm over ssh/scp (no condor_ft-gahp)
supported_lrms=slurm
blah_libexec_directory=$PREFIX/libexec
blah_shared_directories=/
blah_disable_wn_proxy_renewal=yes
blah_delegate_renewed_proxies=no
blah_disable_limited_proxy=yes
blah_max_threaded_cmds=20
#blah_debug_save_submit_info=$PREFIX/debug

sshslurm_host=$HOST
sshslurm_key=${KEY}
sshslurm_remote_base=${REMOTE_BASE}
sshslurm_multiplex=$MULTIPLEX
sshslurm_cleanup=yes
sshslurm_state_dir=$PREFIX/jobs
EOF

# ---- blahpd wrapper (points the stock binary at the private config) --------
cat > "$PREFIX/bin/blahpd" <<EOF
#!/bin/bash
export BLAHPD_CONFIG_LOCATION=$PREFIX/blah.config
export BLAHPD_LOCATION=$PREFIX
exec $stock_blahpd "\$@"
EOF
chmod +x "$PREFIX/bin/blahpd"

# ---- HTCondor knob: route "batch slurm" (local) to the wrapper -------------
snippet="# grid_resource = batch slurm  ->  ssh/scp Slurm blahp for $HOST
# (no user@host in grid_resource => no remote_gahp, no condor_ft-gahp)
SLURM_GAHP = $PREFIX/bin/blahpd"
if [ -n "$CONDOR_CFG" ]; then
    echo "$snippet" > "$CONDOR_CFG"
    echo "wrote $CONDOR_CFG -- now run: condor_reconfig"
else
    echo; echo "Add this to /etc/condor/config.d/60-vortex-sshslurm.config, then condor_reconfig:"
    echo "$snippet"
fi

# ---- smoke test -------------------------------------------------------------
echo; echo "ping test (ssh + squeue on $HOST):"
BLAHPD_CONFIG_LOCATION=$PREFIX/blah.config "$PREFIX/libexec/slurm_ping.sh" || true
