# Ghub Pegasus WMS Tutorial and Templates 

This Jupyter Notebook tool repository provides an introductory tutorial and templates for running [Pegasus Workflow Management System (WMS)](https://pegasus.isi.edu) workflows for Ghub and provides Pegasus pipeline workflow templates that associates two simple workflow jobs to create a "Hello World" demonstration of Pegasus. 

The repository contains a Dockerfile for JupyterHub DockerSpawner, which enables JupyterHub to provision an individual user notebook server within isolated Docker containers for the tool.

- Templates are  provided for workflow jobs written in the `Bash`, `C`, `CPP`, `Fortran`, `MATLAB`, `Python` and `R` programming languages. Each programming language requires a different template because the scripts to launch the `Bash`, `Python`, and `R` scripts, and the scripts to build and launch the binary executables for the `C`, `CPP`, `Fortran`, and `MATLAB` source codes, are different for each programming language. The templates' scripts and source codes provide a guideline for you to create your Pegasus WMS workflow tool for Ghub.  

- `Python` template testing completed. TODO: test the `Bash`, `C`, `CPP`, `Fortran`, `MATLAB` and `R` templates.  

- The Pegasus WMS comprises software that automates and manages the execution of computational workflow jobs, including staging the jobs, distributing the work, submitting the jobs for execution, and handling data flow dependencies and overcoming job failures. The workflow jobs are executed on the University at Buffalo (UB)'s [Center for Computational Research (CCR)](https://www.buffalo.edu/ccr.html) high-performance compute cluster, UB-HPC. Using a process method and bash scripts provided by Anthropic Claude to implement a [deployment scenario](https://pegasus.isi.edu/documentation/user-guide/deployment-scenarios.html) more similar to the Pegasus WMS's NERSC Superfacility API Integration (SFAPI) deployment scenario. UB-HPC disables port forwarding, so the Pegasus WMS, remote HPC cluster, job submission via SSH, deployment scenario, utilizing HTCondor's condor_remote_cluster tool, does not work for UB-HPC. 

## One-Time Setup

- The configure_tool.sh bash script requires that you have previouly generated and uploaded a ssh key pair for UB-HPC access. Please see [Login Node](https://docs.ccr.buffalo.edu/en/latest/hpc/login/) or more information.


## Usage

### Build the Docker Image

- source ./configure_tool.sh
- source ./build_tool.sh ghubex1

### Launch a Jupyter Notebook stored locally using JupyterHub DockerSpawner

- Off campus, connect to Cisco VPN, then log in using your group UBVPN credentials.
- source ./launch_tool.sh ghubex1 to start a JupyterHub and Server and run the Docker image. This runs a single-user JupyterHub and Server using the jupyterhub.auth.DummyAuthenticator for development testing only.

### Login to JupyterHub

When the *JupyterHub is now running at...*  message appears, open a web browser and enter the URL: localhost\:8000, sign in with username: jovyan, password is not required. DockerSpawner will take the authenicated user and spin up an individual, isolated single-user notebook server inside a Docker container. Open the tool's ghubex1.ipynb Jupyter notebook and select Restart Kernel and Run All Cells.

Follow the processing steps in ghubex1.ipynb to launch and run the workflow.

### Logout of JupyterHub
   
Logout of the Jupyter notebook.

Enter Control-C to stop the JupyterHub and Server.

Enter source ./remove_tool.sh <tool_alias_name> to remove any containers, volumes and images created for the tool.

### Workflow Results

- Results and interim files generated for running a workflow are stored in the mounted ./submithost//LOCAL/shared-storage directory.


