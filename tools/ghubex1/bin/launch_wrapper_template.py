#---------------------------------------------------------------------------------------------------
# launch_wrapper.py
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: ghubex1.ipynb
# Purpose: Plan and submit a Pegasus WMS workflow
# Author: Renette Jones-Ivey, August Skies, LLC
# Date: October, 2026
# References: https://pegasus.isi.edu/documentation/user-guide/deployment-scenarios.html and
#    Anthropic Claude
#---------------------------------------------------------------------------------------------------

import ast
import boto3
import configparser
import datetime
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
#from datetime import datetime

import hublib.cmd
#help (hublib.cmd.command.executeCommand)

# API for generating Pegasus YAML files
from Pegasus.api import *

# Configuration parameters
import configuration as cfg

class LaunchWrapper():
    
    def __init__(self, template_index, user, lunch_items):

        # Create a logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        self.logger = logger
        self.workingdir = '.'
        self.bindir ='.'
        self.scriptsdir = './pegasus-wms-scripts'
        self.datadir = '.'
        self.examplesdir = '.'
        self.workflow_results_directory = os.path.join('.', 'LOCAL', 'shared-storage')
        self.num_simulations = 1
        self.maxwalltime = 10 #min
        self.template_index = template_index
        self.user = user
        self.lunch_items = lunch_items
 
        '''
        print('self.template_index: ', self.template_index)
        print('self.user: ', self.user)
        print('self.lunch_items: ', self.lunch_items)
        '''

    def display_output (self, message):
        print (message)
        self.logger.info (message)
                
    def subprocess_popen (self, subprocess_args):

        #https://stackoverflow.com/questions/21953835/run-subprocess-and-print-output-to-logging
        #https://stackoverflow.com/questions/5631624/how-to-get-exit-code-when-using-python-subprocess-communicate-method
        subprocess_result = subprocess.Popen(subprocess_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #print ('type(subprocess_result): ', type(subprocess_result)) #<class 'subprocess.Popen'>
        subprocess_output, _ =  subprocess_result.communicate() # Wait for and communicate output
        returncode = subprocess_result.returncode
        #print ('type(subprocess_output): ', type(subprocess_output)) #<class 'bytes'>
        #print ("type(returncode): ", type (returncode)) #<class 'int'>
        decoded_string = subprocess_output.decode('utf-8')  # Or the appropriate encoding
        lines = decoded_string.splitlines()
        for line in lines:
            print(line)
        return returncode
    
    def run_workflow(self):

        try:
        
            print ('LaunchWrapper.run_workflow...')
            
            template =  cfg.TEMPLATE_LIST[self.template_index]
            print ('template: %s' %template)

            TOPDIR = os.getcwd()
            os.environ['TOPDIR'] = TOPDIR
            self.logger.info("os.environ['TOPDIR']: %s" %str(os.environ['TOPDIR']))
            os.environ["CONDOR_CONFIG"] = "/etc/condor/condor_config"             
            self.logger.info("os.environ['CONDOR_CONFIG']: %s" %str(os.environ['CONDOR_CONFIG']))
             
            #BIN_DIR=`pegasus-config --bin`
            #echo "BIN_DIR: "$BIN_DIR
            #PEGASUS_LOCAL_BIN_DIR=${BIN_DIR}
            #export PEGASUS_LOCAL_BIN_DIR
            PEGASUS_LOCAL_BIN_DIR = '/usr/bin'
            os.environ['PEGASUS_LOCAL_BIN_DIR'] = PEGASUS_LOCAL_BIN_DIR
            self.logger.info("os.environ['PEGASUS_LOCAL_BIN_DIR']: %s" %str(os.environ['PEGASUS_LOCAL_BIN_DIR']))
            
    	    # Define execution environment settings
            SSH_KEY_PATH = str(Path.home() / ".ssh/id_ed25519")
            REMOTE_SCRATCH_DIR = f"/vscratch/grp-ghub/VORTEX_USER-temp/pegasus-scratch"
            os.environ['REMOTE_SCRATCH_DIR'] = REMOTE_SCRATCH_DIR
            self.logger.info("os.environ['REMOTE_SCRATCH_DIR']: %s" %str(os.environ['REMOTE_SCRATCH_DIR']))
    
            ########################################################################
            # Create and plan the Pegasus WMS workflow
            ########################################################################

            workflow_name = 'ghubex1_%s_launch_workflow_%s' %(template, self.user)
            #print ('workflow_name: ', workflow_name)
            wf = Workflow(workflow_name)
            #print ('wf: ', wf)

            ########################################################################
            # Create the Site Catalog
            ########################################################################

            #'''
            sc = SiteCatalog()
            wf.add_site_catalog(sc)

            # Local Host PC Site (Where Pegasus planner & HTCondor run)
            local_site = Site("local", arch=Arch.X86_64, os_type=OS.LINUX)
            local_site.add_directories(
                Directory(Directory.SHARED_SCRATCH, path="%s/LOCAL/shared-storage" %TOPDIR)
                .add_file_servers(FileServer("file://%s/LOCAL/shared-storage" %TOPDIR, Operation.ALL)),
                Directory(Directory.LOCAL_STORAGE, path="%s/LOCAL/shared-storage" %TOPDIR)
                .add_file_servers(FileServer("file://%s/LOCAL/shared-storage" %TOPDIR, Operation.ALL))
            )
            local_site.add_profiles(
                Namespace.PEGASUS, key="SSH_PRIVATE_KEY", value=SSH_KEY_PATH
            )
            sc.add_sites(local_site)

            # Remote HPC (Vortex) Execution Site,
            # Ubuntu 24.04 (cat /etc/os-release); must match so Pegasus stages the right worker package
            vortex_site = Site("vortex", arch=Arch.X86_64, os_type=OS.LINUX, os_release="ubuntu", os_version="24")
            vortex_site.add_directories(
                Directory(Directory.SHARED_SCRATCH, path=REMOTE_SCRATCH_DIR, shared_file_system=True)
                .add_file_servers(FileServer(f"scp://VORTEX_USER@VORTEX_HOST/vscratch/grp-ghub/VORTEX_USER-temp/pegasus-scratch", Operation.ALL)),
            )
            vortex_site.add_profiles(
                # NO user@host here: local blahpd (SLURM_GAHP wrapper), no ft-gahp
                Namespace.CONDOR, grid_resource="batch slurm"
            )
            # #SBATCH options added for vortex added directly to Path.home()/vortex-sshslurm-blahpd/libexec/slurm_submit.sh 
            vortex_site.add_profiles(
                Namespace.PEGASUS, 
                style="glite",
                data_configuration="nonsharedfs",
                project="grp-ghub",
                runtime="1800",                      # seconds -> #SBATCH -t
                cores="1",
                memory="2048",
            )
            sc.add_sites(vortex_site)
   
            ########################################################################
            # Create and configure the Transformation Catalog
            ########################################################################

            tc = TransformationCatalog()
            wf.add_transformation_catalog(tc)
            
            # Add the launch script to the Transformation Catalog. The launch script is run on CCR via SLURM.
             
            tooldir = os.path.dirname(os.path.dirname(os.path.realpath(os.path.abspath(__file__))))
            #print ('tooldir: ', tooldir)
            workingdir = os.getcwd()
            #print ('workingdir: ', workingdir)
            
            launch_exec_path =  os.path.join(workingdir, 'remotebin', template, '%s_Launch.sh' %template)
            print ("launch_exec_path: %s" %launch_exec_path)
            '''
            launch_exec = Transformation(
                '%sLaunch' %template,
                site='local',
                pfn=launch_exec_path,
                is_stageable = True, #Stageable or installed
                arch=Arch.X86_64,
                os_type=OS.LINUX)
                #os_release="rhel")
        		# An executable that runs on the remote cluster
        		# Using a system binary like 'wc' already present on Vortex for demonstration
            '''
            launch_exec = Transformation(
        	    name='%sLaunch' %template,
                site="local",
          	    pfn=launch_exec_path,
        	    is_stageable=True,
          	    version="1.0",
                arch=Arch.X86_64,
                os_type=OS.LINUX,
                os_release="ubuntu",
                os_version="24"
            )
            tc.add_transformations(launch_exec)
            
            ########################################################################
            # Create and configure the Replica Catalog
            ########################################################################

            rc = ReplicaCatalog()
            wf.add_replica_catalog(rc)

            # PFNs:

            # All files in a Pegasus workflow are referred to in the DAX using their Logical File Name (LFN).
            # These LFNs are mapped to Physical File Names (PFNs) when Pegasus plans the workflow.
            # Add input files to the DAX-level replica catalog

            # Create the f.a input file for the first workflow job
            
            f_a_filepath = os.path.join(workingdir, 'f.a')
            print ('f_a_filepath: %s' %f_a_filepath)
            fp = open(f_a_filepath,'w')
            if fp:
               fp.write('{0}\n'.format(self.lunch_items.rstrip()))
               fp.close()
            else:
               print ('Could not create the %s input file.\n' %f_a_filepath)
               return 1

            jobs_dir = os.path.join('bin', template)
            job1 = cfg.JOB1_LIST[self.template_index]
            job2 = cfg.JOB2_LIST[self.template_index]
    
            job1filepath = os.path.join(tooldir, jobs_dir, job1)
            print ('job1filepath: %s' %job1filepath)
            rc.add_replica('local', File(job1), job1filepath)
            job2filepath = os.path.join(tooldir, jobs_dir, job2)
            print ('job2filepath: %s' %job2filepath)
            rc.add_replica('local', File(job2), job2filepath)
            rc.add_replica('local', File('f.a'), f_a_filepath)

            ########################################################################
            # Add jobs to the workflow
            ########################################################################

            # On Ghub, .add_outputs register_replica must be set to False (the default is True) to prevent
            # Pegasus from returning with a post script failure.
            
            workflow_job1 = Job(launch_exec)\
                .add_args("""%s %s""" %(job1, self.user))\
                .add_inputs(File(job1))\
                .add_inputs(File('f.a'))\
                .add_outputs(File('f.b'), stage_out=True, register_replica=False)\
                .add_metadata(time='%d' %self.maxwalltime)
            wf.add_jobs(workflow_job1)

            workflow_job2 = Job(launch_exec)\
                .add_args("""%s""" %job2)\
                .add_inputs(File(job2))\
                .add_inputs(File('f.b'))\
                .add_outputs(File('f.c'), stage_out=True, register_replica=False)\
                .add_metadata(time='%d' %self.maxwalltime)
            wf.add_jobs(workflow_job2)
            
            # job2 depends on job1 completing
            
            wf.add_dependency(workflow_job2, parents=[workflow_job1])

            ########################################################################
            # Create the YAML (YAML Ain't Markup Language) file
            ########################################################################

            try:
                wf.write('launch_workflow.yml')
            except PegasusClientError as e:
                print(str(e))
                return 1

            # Verify contents
            #fp = open('workflow.yml', 'r')
            #file_contents = fp.read()
            #print (file_contents)
            #fp.close()
            
            sys.stdout.flush()

            utcnow = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            prefix = 'remotehost-' + utcnow
            print ('prefix: %s' %prefix)

            ########################################################################
            # Submit the Pegasus Workflow plan
            ########################################################################

            try:

                self.display_output ('Planning the workflow...')
        		# Plan parameters configure the runtime options 
        		# Pegasus automatically handles Condor File I/O staging over the SSH tunnel
                wf.plan(conf='./pegasusrc',\
                    cluster = ['horizontal'],\
                    sites = ['vortex'],\
                    output_sites = ['local'],\
                    dir = './dags',\
                    force = True,\
                    submit = False
                )
    
                submit_dir = wf.braindump.submit_dir
                self.logger.info ('submit_dir: %s' %str(submit_dir))
    
                if os.path.exists(submit_dir):
                        
                    #'''
                    self.display_output ('Running the workflow...')
                    wf.run()
                    self.logger.info ('wf.run_output: %s\n' %str(wf.run_output))
                        
                    self.display_output ('Waiting for the workflow to complete...')
                    wf.wait()
                    #'''
                            
                    script_path = os.path.join(self.scriptsdir,"pegasus-analyzer.sh")
                    self.logger.info ('Calling %s...' %script_path)
                    subprocess_args = [script_path,self.workflow_results_directory,submit_dir]
                    returncode = self.subprocess_popen(subprocess_args)
                    if returncode != 0:
                        self.logger.warning ('pegasus-analyzer.sh returned nonzero returncode: %s' %str(returncode))
    
                    script_path = os.path.join(self.scriptsdir,"pegasus-statistics.sh")
                    self.logger.info ('Calling %s...' %script_path)
                    subprocess_args = [script_path,self.workflow_results_directory,submit_dir]
                    returncode = self.subprocess_popen(subprocess_args)
                    if returncode != 0:
                        self.logger.warning ('pegasus-statistics.sh returned nonzero returncode: %s' %str(returncode))
    
                    # Clean up
                            
                    self.display_output("Cleanup...")
    
                    shutil.rmtree(submit_dir)
                    return 0
                            
                else:
                    self.logger.error ('launch_wrapper.py run_workflow: Pegasus submit directory %s not created' %submit_dir)
                    return 1
                    
            except PegasusClientError as e:
            
                print ('launch_wrapper.py run_workflow: PegasusClientError Exception: %s\n' %str(e))
                return 1

        except Exception as e:
            
            print ('LaunchWrapper Exception: %s\n' %str(e))
            return 1
