#!/usr/bin/env python3
"""
Pegasus 5.1.3 workflow: submit host (JupyterHub container, HTCondor 24.0.24)
-> vortex.ccr.buffalo.edu Slurm, nonsharedfs, NO condor_ft-gahp.

Key points
  * Site "vortex" uses style=glite with an explicit
        condor profile grid_resource = "batch slurm"      (no user@host)
    so HTCondor runs the LOCAL blahp (SLURM_GAHP wrapper from install.sh),
    which ssh/scp's to vortex itself. style=ssh cannot be used: Pegasus'
    SSH style always writes "batch slurm <contact>", and any contact makes
    HTCondor start condor_ft-gahp over `ssh -R`.
  * Data: nonsharedfs, staging site = vortex's own scratch, reached with
    scp:// from the submit host (pegasus-transfer, plain scp, no forwarding).
    Compute jobs (PegasusLite) then symlink from that scratch.
  * Pegasus is not installed on vortex -> the worker package is staged.

Edit the CONFIG block, then:  python3 workflow.py && pegasus-plan ...
(see the planning command at the bottom).
"""
import os
from pathlib import Path

from Pegasus.api import (
    Arch, Directory, File, FileServer, Job, Namespace, OS, Operation,
    Properties, ReplicaCatalog, Site, SiteCatalog, Transformation,
    TransformationCatalog, Workflow,
)

# ---------------- CONFIG ----------------
REMOTE_USER = "jdoe"                                   # your vortex login
REMOTE_HOST = "vortex.ccr.buffalo.edu"
SSH_KEY = str(Path.home() / ".ssh/id_ed25519")          # IDM-registered key, no passphrase
REMOTE_SCRATCH = f"/vscratch/grp-lab/{REMOTE_USER}/pegasus-scratch"
SLURM_PARTITION = "general-compute"
SLURM_QOS = "general-compute"
SLURM_ACCOUNT = "grp-lab"
# ----------------------------------------

TOP = Path(__file__).resolve().parent
WORK = TOP / "work"
(TOP / "inputs").mkdir(exist_ok=True)
(TOP / "bin").mkdir(exist_ok=True)

# ---------------- properties ----------------
props = Properties()
props["pegasus.data.configuration"] = "nonsharedfs"
props["pegasus.transfer.worker.package"] = "true"     # no Pegasus on vortex
props["pegasus.transfer.links"] = "true"              # symlink from staging scratch on vortex
props["pegasus.metrics.app"] = "vortex-ssh-demo"
props.write(str(TOP / "pegasus.properties"))

# ---------------- sites ----------------
local = Site("local", arch=Arch.X86_64, os_type=OS.LINUX)
local.add_directories(
    Directory(Directory.SHARED_SCRATCH, str(WORK / "scratch"))
        .add_file_servers(FileServer(f"file://{WORK}/scratch", Operation.ALL)),
    Directory(Directory.LOCAL_STORAGE, str(TOP / "outputs"))
        .add_file_servers(FileServer(f"file://{TOP}/outputs", Operation.ALL)),
)
# key used by pegasus-transfer (stage-in/out, create-dir, cleanup jobs run here)
local.add_profiles(Namespace.PEGASUS, key="SSH_PRIVATE_KEY", value=SSH_KEY)

vortex = Site("vortex", arch=Arch.X86_64, os_type=OS.LINUX,
              os_release="ubuntu", os_version="24")
vortex.add_directories(
    Directory(Directory.SHARED_SCRATCH, REMOTE_SCRATCH, shared_file_system=True)
        .add_file_servers(FileServer(
            f"scp://{REMOTE_USER}@{REMOTE_HOST}{REMOTE_SCRATCH}", Operation.ALL)),
)
# NOTE: no add_grids(...) and no style=ssh. The grid_resource below is what
# keeps HTCondor away from remote_gahp / condor_ft-gahp.
vortex.add_pegasus_profile(
    style="glite",
    data_configuration="nonsharedfs",
    queue=SLURM_PARTITION,
    project=SLURM_ACCOUNT,
    runtime="3600",                      # seconds -> #SBATCH -t
    cores=1,
    memory="2 GB",
    glite_arguments=f"--qos={SLURM_QOS}",
)
vortex.add_condor_profile(grid_resource="batch slurm")

sc = SiteCatalog().add_sites(local, vortex)
sc.write(str(TOP / "sites.yml"))

# ---------------- transformations ----------------
# (a) script that lives on the submit host -> staged to vortex by Pegasus
preprocess_sh = TOP / "bin/preprocess.sh"
if not preprocess_sh.exists():
    preprocess_sh.write_text("#!/bin/bash\nset -e\nhostname\ntr a-z A-Z < \"$1\" > \"$2\"\n")
    preprocess_sh.chmod(0o755)

preprocess = Transformation(
    "preprocess",
    site="local",
    pfn=f"file://{preprocess_sh}",
    is_stageable=True,                   # Pegasus copies it; HTCondor does not
    arch=Arch.X86_64, os_type=OS.LINUX,
    os_release="ubuntu", os_version="24",
).add_pegasus_profile(runtime="600", cores=1, memory="1 GB")

# (b) executable already installed on vortex -> not staged
analyze = Transformation(
    "analyze",
    site="vortex",
    pfn="/usr/bin/wc",                   # replace with your installed code path
    is_stageable=False,
).add_pegasus_profile(runtime="1800", cores=1, memory="2 GB")

tc = TransformationCatalog().add_transformations(preprocess, analyze)
tc.write(str(TOP / "transformations.yml"))

# ---------------- replicas ----------------
raw_path = TOP / "inputs/raw.txt"
if not raw_path.exists():
    raw_path.write_text("hello vortex\n")
rc = ReplicaCatalog().add_replica("local", "raw.txt", f"file://{raw_path}")
rc.write(str(TOP / "replicas.yml"))

# ---------------- workflow ----------------
raw, upper, counts = File("raw.txt"), File("upper.txt"), File("counts.txt")
wf = Workflow("vortex-ssh-demo")
wf.add_jobs(
    Job(preprocess).add_args(raw, upper).add_inputs(raw).add_outputs(upper, stage_out=False),
    Job(analyze).add_args("-c", upper).add_inputs(upper)
        .set_stdout(counts, stage_out=True, register_replica=False),
)
wf.write(str(TOP / "workflow.yml"))

print(f"""catalogs written to {TOP}

plan + submit:
  pegasus-plan --conf pegasus.properties \\
      --sites vortex --staging-site vortex=vortex --output-sites local \\
      --dir {WORK}/submit --cleanup leaf --submit workflow.yml

check the generated submit files contain   grid_resource = batch slurm
(and nothing after 'slurm'):
  grep -r grid_resource {WORK}/submit | head
""")
