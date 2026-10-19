# Pegasus 5.1.3 + HTCondor 24.0.24 on vortex without condor_ft-gahp

There is no knob to turn the ft-gahp off. In `src/condor_gridmanager/infnbatchjob.cpp`
(v24.0.24 and current main), `INFNBatchJob::INFNBatchJob()` creates `m_xfer_gahp`
(REMOTE_GAHP ... `condor_ft-gahp`) whenever `grid_resource` has anything after the batch
type (`user@host`). `GM_TRANSFER_INPUT`/`GM_TRANSFER_OUTPUT` then use it for every job with
`GahpIsRemote()`. `INFNBatchResource` also fails its ping if the ft-gahp won't start.
Empty `transfer_input_files`, `should_transfer_files = NO` and `transfer_executable = false`
don't change this.

You have two ways around it.

## Option A (recommended): local blahpd + ssh/scp Slurm plugin  -> `optionA-local-blahp/`

`grid_resource = batch slurm` (no user@host) makes the gridmanager run blahpd locally. Then
no ft-gahp starts and nothing needs port forwarding. A private blahp libexec swaps the stock
`slurm_*.sh` for versions that `ssh`/`scp` to vortex. This is the design Pegasus 5.1.3 ships
for NERSC (`share/pegasus/htcondor/glite/sfapi_*.sh`, `style: glite`, nonsharedfs).

1. `./install.sh USER@vortex.ccr.buffalo.edu /vscratch/grp-GRP/USER/blahp_jobs ~/.ssh/id_ed25519`
2. Add `SLURM_GAHP = ~/.ssh-blahp/bin/blahpd-ssh` (see `condor_config.d-60-ssh-blahp.conf`)
   and run `condor_reconfig`.
3. Run `slurm_ping.sh` (install.sh prints the exact command). It should print `0 No error`.
4. Use `pegasus/sites.yml` + `pegasus/pegasus.properties` (`style: glite`,
   `condor.grid_resource: batch slurm`, `data.configuration: nonsharedfs`).

## Option B: keep `style: ssh`, replace only the ft-gahp  -> `optionB-ftgahp-shim/`

`REMOTE_GAHP` is a config knob. `remote_gahp_noft` sends `blahpd` to the stock
`remote_gahp` (plain ssh, which already passes `condor_remote_cluster --test`). It sends
`condor_ft-gahp` to `ftgahp_scp.py`, which speaks the ft-gahp GAHP protocol and moves the
sandbox with scp from the submit host.

1. Copy `remote_gahp_noft` and `ftgahp_scp.py` to `~/.ftgahp-scp/`.
2. Run `condor_config_val REMOTE_GAHP` and note the result. Then add
   `condor_config.d-60-ftgahp-scp.conf` with the paths and base dir filled in, and run
   `condor_reconfig`.
3. Use `pegasus/sites.yml` (`style: ssh`, nonsharedfs). Copy Pegasus'
   `$PEGASUS_SHARE_DIR/htcondor/glite/slurm_local_submit_attributes.sh` to
   `~/.blah/slurm_local_submit_attributes.sh` on vortex. The blahp checks `~/.blah/` first,
   whatever the bosco layout is.
4. Log: `~/.ftgahp_scp.log`.

## Both options

* Staging site = vortex scratch with `sharedFileSystem: true` and an `scp://` file server.
  Stage-in/out and cleanup jobs run on the submit host with scp, and PegasusLite on the
  compute nodes uses the filesystem path.
* `pegasus.transfer.worker.package = true`, because vortex has no Pegasus. The vortex site is
  set to `os.release: ubuntu`, `os.version: '24'` (Ubuntu 24.04.5). If the submit image is
  also Ubuntu 24.04, Pegasus builds the worker package from the local install.
* Replace the placeholders USER, GRP, partition, qos and account.
* Both options were run against mocked ssh/scp/sbatch/squeue/sacct (submit -> running ->
  done -> outputs back -> remote dir cleaned; cancel; ping; a full ft-gahp GAHP session).
  They have not been run against vortex or a live gridmanager yet.
