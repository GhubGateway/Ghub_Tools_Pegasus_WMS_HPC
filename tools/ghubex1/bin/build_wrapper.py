#---------------------------------------------------------------------------------------------------
# build_wrapper.py
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: ghubex1.ipynb
# Also see Ghub, https://theghub.org/about
# Purpose: Plan and submit a Pegasus WMS Workflow to build binary executables on CCR
# Author: Renette Jones-Ivey
# Date: July 2024
# Reference: https://pegasus.isi.edu/documentation
#---------------------------------------------------------------------------------------------------

import ast
import os
import sys
#import glob

import hublib.cmd
#help (hublib.cmd.command.executeCommand)

# API for generating Pegasus YML files
from Pegasus.api import *

# Configuration parameters
import configuration as cfg

class BuildWrapper():
    
    def __init__(self, template_index, user):

        self.template_index = template_index
        self.user = user
        self.maxwalltime = 30 # minutes

        '''
        print('self.template_index: ', self.template_index)
        print('self.user: ', self.user)
        '''

    def run_workflow(self):

        try:

            print ('BuildWrapper.run_workflow...')

            template =  cfg.TEMPLATE_LIST[self.template_index]
            print ('template: %s' %template)
            
            ########################################################################
            # Create and plan the Pegasus WMS workflow
            ########################################################################

            workflow_name = 'ghubex1_%s_build_workflow_%s' %(template, self.user)
            #print ('workflow_name: ', workflow_name)
            wf = Workflow(workflow_name)
            #print ('wf: ', wf)

            ########################################################################
            # Create and configure the Transformation Catalog
            ########################################################################

            tc = TransformationCatalog()
            wf.add_transformation_catalog(tc)
            
            # Add the build script to the Transformation Catalog. The build script is run on CCR via SLURM.
            # The build script contains specific instructions for compiling the executables
                
            # For the installed version of the tool, this resolves to /apps/ghubex1/r<revision number>
            tooldir = os.path.dirname(os.path.dirname(os.path.realpath(os.path.abspath(__file__))))
            #print ('tooldir: ', tooldir)
            workingdir = os.getcwd()
            #print ('workingdir: ', workingdir)

            build_exec_path =  os.path.join(tooldir, 'remotebin', template, '%s_Build.sh' %template)
            print ("build_exec_path: %s" %build_exec_path)
            
            build_exec = Transformation(
                '%sBuild' %template,
                site='local',
                pfn=build_exec_path,
                is_stageable = True, #Stageable or installed
                arch=Arch.X86_64,
                os_type=OS.LINUX,
                os_release="rhel")

            tc.add_transformations(build_exec)
            
            ########################################################################
            # Create the Replica Catalog
            ########################################################################

            rc = ReplicaCatalog()
            wf.add_replica_catalog(rc)

            # All files in a Pegasus workflow are referred to in the DAX using their Logical File Name (LFN).
            # These LFNs are mapped to Physical File Names (PFNs) when Pegasus plans the workflow.
            # Add input files to the DAX-level replica catalog
            
            ########################################################################
            # Configure the Replica Catalog and add the build job to the workflow
            ########################################################################

            srccodedir =  os.path.join(tooldir, 'bin', template)
            srcfiles = [cfg.CODE1_LIST[self.template_index], cfg.CODE2_LIST[self.template_index]]
            binfiles = [cfg.BIN1_LIST[self.template_index], cfg.BIN2_LIST[self.template_index]]

            # On Ghub, .add_outputs register_replica must be set to False (the default is True) to prevent
            # Pegasus from returning with a post script failure.

            build_job = Job(build_exec)\
                .add_metadata(time='%d' %self.maxwalltime)

            for i in range(len(srcfiles)):
            
                srcfile = srcfiles[i]
                srcfilepath = os.path.join(srccodedir, '%s' %srcfile)
                print ('srcfilepath [%d]: %s' %(i, srcfilepath))
                rc.add_replica('local', File('%s' %srcfile), srcfilepath)
                build_job.add_inputs(File('%s' %srcfile))
            
            for i in range(len(binfiles)):
                
                # Executables are returned to the working directory and ghubex1.ipynb
                # moves the executables to the bin directory when the workflow completes,
                binfile = binfiles[i]
                print ('binfile [%d]: %s' %(i, binfile))
                build_job.add_outputs(File('%s' %binfile), stage_out=True, register_replica=False)
                
            wf.add_jobs(build_job)

            ########################################################################
            # Create the YAML (YAML Ain't Markup Language) file
            ########################################################################

            try:
                wf.write('build_workflow.yml')
            except PegasusClientError as e:
                print(e)
                return 1

            # Verify contents
            #fp = open('workflow.yml', 'r')
            #file_contents = fp.read()
            #print (file_contents)
            #fp.close()
            
            sys.stdout.flush()
            
            #########################################################
            # Submit the Pegasus Workflow Plan
            #########################################################
    
            #'''
            submitcmd = ['submit', '--venue', 'WF-vortex-ghub', 'pegasus-plan', '--dax', 'build_workflow.yml']
            #print ('submitcmd: ', submitcmd)

            # submit blocks.
            exitCode,pegasusStdout,pegasusStderr = hublib.cmd.command.executeCommand(submitcmd,streamOutput=True)

            if (exitCode == 0):

                return 0

            else:
            
                # In this case, look for .stderr and .stdout files in the work directory
                print ('buildWrapper.py: hublib.cmd.command.executeCommand(%s) returned with a non zero exit code = %d\n' %(submitcmd, exitCode))
                files = os.listdir(workingdir)
                files.sort(key=lambda x: os.path.getmtime(x))
                for file in files:
                    # Get the numbered Pegasus work directory
                    #print ('type(file): ', type(file)) #<class 'str'>
                    if os.path.isfile(file) and file[0].isdigit() and file.endswith('.stderr'):
                        print ('stderr file: %s\n' %os.path.join(workingdir, file))
                        print ('For the ghubex1 tool, the following errors were returned while running a Pegasus workflow: ')
                        with open(file) as f:
                            lines = f.readlines()
                            for line in lines:
                                if 'WARNING' not in line:
                                    print (line)
                        # In case there is more than one stderr file
                        break
                return exitCode
            #'''
             
        except Exception as e:
            
            print ('buildWrapper.py Exception: %s\n' %str(e))
            return 1

