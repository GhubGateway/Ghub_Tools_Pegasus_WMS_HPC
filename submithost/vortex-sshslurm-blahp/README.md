# Pegasus -> vortex Slurm without condor_ft-gahp

HTCondor (24.0 and current main) always starts condor_ft-gahp through
`remote_gahp` (`ssh -R`) when grid_resource has a `user@host`. No knob disables it.
This kit makes the blahp LOCAL (`grid_resource = batch slurm`) and has the blahp
scripts use plain ssh/scp to vortex instead.

1. `./install.sh --host jdoe@vortex.ccr.buffalo.edu --key ~/.ssh/id_ed25519 \
       --remote-base /vscratch/grp-lab/jdoe/blahp_jobs`
   then put the printed `SLURM_GAHP = ...` line in /etc/condor/config.d/ and `condor_reconfig`
   (in the JupyterHub image: bake it into the Dockerfile).
2. Edit the CONFIG block of `workflow.py`, run it, run the printed `pegasus-plan`.
3. Check: `grep -r grid_resource work/submit` shows `batch slurm` with nothing after it.

Debug: uncomment `blah_debug_save_submit_info` in ~/.blahp-sshslurm/blah.config to keep each
generated sbatch script. Gridmanager log: `condor_config_val GRIDMANAGER_LOG`.
