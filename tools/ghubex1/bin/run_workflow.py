    def run_workflow(self, aws_region, aws_iam_username):

        try:

            self.display_output('Configuring the workflow...')
            self.logger.info('aws_region: %s' %aws_region)
            self.logger.info('iam_username: %s' %aws_iam_username)
            
            #########################################################
            # Create environment variables
            #########################################################

            # Create the TOPDIR, PEGASUS_LOCAL_BIN_DIR, S3_URL_PREFIX, S3_BUCKET, and S3_BUCKET_KEY
            # environment variables for ./conf/sites.xml.
            
            TOPDIR = os.getcwd()
            os.environ['TOPDIR'] = TOPDIR
            self.logger.info("os.environ['TOPDIR']: %s" %str(os.environ['TOPDIR']))
            
            #BIN_DIR=`pegasus-config --bin`
            #echo "BIN_DIR: "$BIN_DIR
            #PEGASUS_LOCAL_BIN_DIR=${BIN_DIR}
            #export PEGASUS_LOCAL_BIN_DIRƒ
            PEGASUS_LOCAL_BIN_DIR = '/usr/bin'
            os.environ['PEGASUS_LOCAL_BIN_DIR'] = PEGASUS_LOCAL_BIN_DIR
            self.logger.info("os.environ['PEGASUS_LOCAL_BIN_DIR']: %s" %str(os.environ['PEGASUS_LOCAL_BIN_DIR']))
            
            S3_URL_PREFIX = 's3://user@amazon'
            os.environ['S3_URL_PREFIX'] = S3_URL_PREFIX
            self.logger.info("os.environ['S3_URL_PREFIX']: %s" %str(os.environ['S3_URL_PREFIX']))
            
            # ./pegasusrc sets pegasus.catalog.site.file=./conf/sites.xml.
            # ./conf/sites.xml aws-batch site's file server definition sets url to "${S3_URL_PREFIX}/${S3_BUCKET}/${S3_BUCKET_KEY}"
            # The globally unique S3_BUCKET is created by Pegasus (if it does not already exist), for the current Amazon AWS Partition and IAM user.
            # See https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html for more information on bucket naming rules.
            bucket_name_suffix = re.sub(r'[^a-zA-Z0-9]+', '', str(aws_region + aws_iam_username)).lower()[:63]
            S3_BUCKET = 'titan2d-blm-emulator-%s' %bucket_name_suffix
            #print ('S3_BUCKET: ', S3_BUCKET)
            os.environ['S3_BUCKET'] = S3_BUCKET
            self.logger.info("os.environ['S3_BUCKET']: %s" %str(os.environ['S3_BUCKET']))
            # The S3_BUCKET_KEY (i.e. directory) is created for each workflow run and deleted after each workflow run.
            S3_BUCKET_KEY = 'pegasus-workflow'
            #print ('S3_BUCKET_KEY: ', S3_BUCKET_KEY)
            os.environ['S3_BUCKET_KEY'] = S3_BUCKET_KEY
            self.logger.info("os.environ['S3_BUCKET_KEY']: %s" %str(os.environ['S3_BUCKET_KEY']))
    
            #########################################################
            # Path to the titan and octave launch scripts
            #########################################################

            # Create the Pegasus workflow
            wf = Workflow('emulatorworkflow')
            tc = TransformationCatalog()
            wf.add_transformation_catalog(tc)
            rc = ReplicaCatalog()
            wf.add_replica_catalog(rc)
            
            # Add titan launch script and input files to the DAX-level transformation catalog
                
            titanlaunch = Transformation(
                'titanlaunch',
                site='local',
                pfn=os.path.join(self.workingdir,'remotebin','titanLaunch.sh'),
                is_stageable = True, #Stageable or installed
                arch=Arch.X86_64,
                os_type=OS.LINUX)\
            .add_profiles(Namespace.PEGASUS, key="clusters_size", value=self.num_simulations) \
            .add_profiles(Namespace.PEGASUS, key="clusters_num", value=self.num_simulations)
            tc.add_transformations(titanlaunch)
            
            octavelaunch = Transformation(
                'octavelaunch',
                site='local',
                pfn=os.path.join(self.workingdir,'remotebin','octaveLaunch.sh'),
                is_stageable = True, #Stageable or installed
                arch=Arch.X86_64,
                os_type=OS.LINUX)\
            .add_profiles(Namespace.PEGASUS, key="clusters_size", value=self.num_simulations) \
            .add_profiles(Namespace.PEGASUS, key="clusters_num", value=self.num_simulations)
            tc.add_transformations(octavelaunch)

            #########################################################
            #########################################################

            # PFNs:

            # All files in a Pegasus workflow are referred to in the DAX using their Logical File Name (LFN).
            # These LFNs are mapped to Physical File Names (PFNs) when Pegasus plans the workflow.
            # Add input files to the DAX-level replica catalog

            # Grass database
            grassgis_database_zipped = self.grassgis_database+'.tar.gz'
            self.logger.info ('grassgis_database_zipped: %s' %grassgis_database_zipped)
            # titanlaunch script unzips before titan is invoked
            rc.add_replica("local", File(grassgis_database_zipped), os.path.join(self.workingdir, grassgis_database_zipped))
            
            # Octave scripts
            rc.add_replica("local", File('down_sample_pileheightrecord.m'), os.path.join(self.bindir, 'down_sample_pileheightrecord.m'))
            rc.add_replica("local", File('r_down_sample_pileheightrecord.m'), os.path.join(self.bindir, 'r_down_sample_pileheightrecord.m'))
            rc.add_replica("local", File('r_build_mini_emulator.m'), os.path.join(self.bindir, 'r_build_mini_emulator.m'))
            rc.add_replica("local", File('build_mini_emulator.m'), os.path.join(self.bindir, 'build_mini_emulator.m'))
            rc.add_replica("local", File('r_script11_12_13.m'), os.path.join(self.bindir, 'r_script11_12_13.m'))
            rc.add_replica("local", File('script11_12_13.m'), os.path.join(self.bindir, 'script11_12_13.m'))
            rc.add_replica("local", File('extract_macrosimplex_resample_inputs_P.m'), os.path.join(self.bindir, 'extract_macrosimplex_resample_inputs_P.m'))
            rc.add_replica("local", File('evaluate_mini_emulator_mean.m'), os.path.join(self.bindir, 'evaluate_mini_emulator_mean.m'))
            rc.add_replica("local", File('assemble_minis_to_macro_to_phm_P.m'), os.path.join(self.bindir, 'assemble_minis_to_macro_to_phm_P.m'))
            rc.add_replica("local", File('r_script14.m'), os.path.join(self.bindir, 'r_script14.m'))
            rc.add_replica("local", File('script14.m'), os.path.join(self.bindir, 'script14.m'))
            rc.add_replica("local", File('merge_probability_of_hazard_maps.m'), os.path.join(self.bindir, 'merge_probability_of_hazard_maps.m'))
            
            # Files generated by emulator.ipynb
            rc.add_replica("local", File('uncertain_input_list.txt'), os.path.join(self.workingdir, 'uncertain_input_list.txt'))
            rc.add_replica("local", File('macro_emulator.pwem'), os.path.join(self.workingdir, 'macro_emulator.pwem'))
            rc.add_replica("local", File('macro_resample_assemble.inputs'), os.path.join(self.workingdir, 'macro_resample_assemble.inputs'))
            rc.add_replica("local", File('AZ_vol_dir_bed_int.phm'), os.path.join(self.workingdir, 'AZ_vol_dir_bed_int.phm'))
            rc.add_replica("local", File('step11_12_13_staged_input.txt'), os.path.join(self.workingdir, 'step11_12_13_staged_input.txt'))
            
            for i in range (1, self.num_simulations + 1):
            
                rc.add_replica("local", File('simulation_%06d.py' % i), os.path.join(self.workingdir, 'simulation_%06d.py' % i))
                rc.add_replica("local", File('build_mini_pwem_meta.%06d' % i), os.path.join(self.workingdir, 'build_mini_pwem_meta.%06d' % i))
                
            # Add jobs
            
            step_4_jobs = []
            
            for i in range (1, self.num_simulations + 1):
                
                # Step 3 - Call titan
                #
                # Input(s): simulation.py for the sample
                # Output(s): pileheightrecord.<%06d sample number>
            
                titanjob  = Job(titanlaunch)\
                    .add_args("""-nt 1 simulation_%06d.py""" % i)\
                    .add_inputs(File(grassgis_database_zipped))\
                    .add_inputs(File('simulation_%06d.py' % i))\
                    .add_outputs(File('pileheightrecord.%06d' % i), stage_out=False)\
                    .set_stdout(File('titan2d_%06d.stdout' % i), stage_out=True)\
                    .set_stderr(File('titan2d_%06d.stderr' % i), stage_out=True)\
                    .add_metadata(time="%d" %self.maxwalltime)
                if i==1:
                    titanjob.add_outputs(File('elevation.grid'), stage_out=True)
                
                wf.add_jobs(titanjob)
                
                # Step 4 - Call down_sample_pileheightrecord.m
                #
                # Input(s): uncertain_input_list.txt, pileheightrecord.<%06d sample number>
                # Output(s): down_sampled_data.<%06d sample number>
                #

                octavejob = Job(octavelaunch)\
                    .add_args("""r_down_sample_pileheightrecord.m %s %d""" % (".", i))\
                    .add_inputs(File('r_down_sample_pileheightrecord.m'))\
                    .add_inputs(File('down_sample_pileheightrecord.m'))\
                    .add_inputs(File('uncertain_input_list.txt'))\
                    .add_inputs(File('pileheightrecord.%06d' % i))\
                    .add_outputs(File('down_sampled_data.%06d' % i), stage_out=False)\
                    .add_metadata(time="%d" %self.maxwalltime)
                    
                wf.add_jobs(octavejob)
                
                wf.add_dependency(octavejob, parents=[titanjob])
                
                step_4_jobs.append(octavejob)
                
            # Step 7 - Call build_mini_emulator.m
            #
            # Inputs(s): down_sampled_data.<%06d sample number> files, build_mini_pwem_meta.<%06d sample number>
            # Output(s):  mini_emulator.<%06d sample number>

            step_7_jobs = []
            
            for i in range (1, self.num_simulations + 1):
            
                octavejob = Job(octavelaunch)\
                    .add_args("""r_build_mini_emulator.m %s %d""" % (".", i))\
                    .add_inputs(File('r_build_mini_emulator.m'))\
                    .add_inputs(File('build_mini_emulator.m'))\
                    .add_inputs(File('build_mini_pwem_meta.%06d' % i))\
                    .add_outputs(File('mini_emulator.%06d' % i), stage_out=False)\
                    .add_metadata(time="%d" %self.maxwalltime)
                    
                for j in range (1, self.num_simulations + 1):
                    octavejob.add_inputs(File('down_sampled_data.%06d' % j))\
                    
                wf.add_jobs(octavejob)
                
                # Needs all step 4 jobs to be complete
                wf.add_dependency(octavejob, parents=step_4_jobs)
                
                step_7_jobs.append(octavejob)

            i=self.simplexStart
            remaining = self.numSimplicesRemaining

            # Steps 11-13 - Call script11_12_13.m
            #
            # Input(s): step11_12_13_staged_input.txt, macro_emulator.pwem,
            #   macro_resample_assemble.inputs, AZ_vol_dir_bed_int.phm,
            #   mini_emulator.<%06d sample number> files
            # Output(s): phm_from_eval* files
            
            step_11_12_13_jobs = []
            
            count = 0
            while (i < self.numSimplices):

                begin=i
                if (remaining > 0):
                    end = begin + self.numSimplicesPerProcessor
                    remaining = remaining - 1
                else:
                    end = begin + self.numSimplicesPerProcessor - 1

                octavejob = Job(octavelaunch)\
                    .add_args("""r_script11_12_13.m %s %d %d""" % (".", begin, end))\
                    .add_inputs(File('r_script11_12_13.m'))\
                    .add_inputs(File('script11_12_13.m'))\
                    .add_inputs(File('extract_macrosimplex_resample_inputs_P.m'))\
                    .add_inputs(File('evaluate_mini_emulator_mean.m'))\
                    .add_inputs(File('assemble_minis_to_macro_to_phm_P.m'))\
                    .add_inputs(File('macro_emulator.pwem'))\
                    .add_inputs(File('macro_resample_assemble.inputs'))\
                    .add_inputs(File('AZ_vol_dir_bed_int.phm'))\
                    .add_inputs(File('step11_12_13_staged_input.txt'))\
                    .add_metadata(time="%d" %self.maxwalltime)
                    
                for j in range (1, self.num_simulations + 1):
                    octavejob.add_inputs(File('mini_emulator.%06d' % j))\

                for j in range (begin, end + 1):
                    # phm filenames are 0 or phm_*
                    if (self.phm_filenames[j-1] != "0"):
                        phm_filename = self.phm_filenames[j-1]
                        octavejob.add_outputs(File(phm_filename), stage_out=False)

                count = count + 1
                wf.add_jobs(octavejob)
                
                # Needs all step 7 jobs to be complete
                wf.add_dependency(octavejob, parents=step_7_jobs)
                
                step_11_12_13_jobs.append(octavejob)
                
                i=end+1
             
            self.logger.info ("Number of r_script11_12_13.m jobs added: %d" % count)
            
            # Step 14 - Call script14.m
            #
            # Input(s): AZ_vol_dir_bed_int.phm, phm_from_eval* files
            # Output(s): AZ_vol_dir_bed_int_final.phm
    
            octavejob = Job(octavelaunch)\
                .add_args("""r_script14.m %s""" % ("."))\
                .add_inputs(File('r_script14.m'))\
                .add_inputs(File('script14.m'))\
                .add_inputs(File('merge_probability_of_hazard_maps.m'))\
                .add_inputs(File('AZ_vol_dir_bed_int.phm'))\
                .add_metadata(time="%d" %self.maxwalltime)
                
            for i in range (self.simplexStart, len(self.phm_filenames)):
                # Filenames are 0 or phm_*
                if (self.phm_filenames[i] != "0"):
                    #print ('phm_filenames[%d]: %s'  %(i, self.phm_filenames[i]))
                    phm_filename = self.phm_filenames[i]
                    octavejob.add_inputs(File(phm_filename))
            octavejob.add_outputs(File('AZ_vol_dir_bed_int_final.phm'), stage_out=True)
            
            wf.add_jobs(octavejob)
                
            #Needs all step_11_12_13 jobs to be complete
            wf.add_dependency(octavejob, parents=step_11_12_13_jobs)
            
            # Create the DAX file
            try:
                wf.write()
                wf.graph(include_files=True, label='xform-id', output=os.path.join(self.workflow_results_directory, 'graph.png'))
            except PegasusClientError as e:
                self.logger.error('Wrapper.py run_workflow: PegasusClientError Exception: %s\n' %str(e))
                return False

            utcnow = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            prefix = 'remotehost-' + utcnow
            self.logger.info ('prefix: %s' %prefix)
                
            try:

                script_path = os.path.join(self.scriptsdir,"pegasus-aws-batch-create.sh")
                self.logger.info ('Calling %s...' %script_path)
                subprocess_args = [script_path,self.workingdir,prefix]
                returncode = self.subprocess_popen(subprocess_args)

                if returncode == 0:
                
                    self.display_output ('Planning the workflow...')
                    wf.plan(conf='./pegasusrc',\
                            cluster = ['horizontal'],\
                            sites = ['aws-batch'],\
                            output_sites = ['local'],\
                            dir = './dags',\
                            force = True,\
                            submit = False)

                    submit_dir = wf.braindump.submit_dir
                    self.logger.info ('submit_dir: %s' %str(submit_dir))

                    if os.path.exists(submit_dir):
                    
                        #'''
                        self.display_output ('Running for the workflow...')
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

                        for i in range (1, 5):
                            filename = "elevation%d.tif" %i
                            filepath = os.path.join(self.workingdir,filename)
                            if (os.path.exists(filepath) == True):
                                os.remove(filepath)
                                
                        for i in range (1, self.num_simulations + 1):
                            filename = "build_mini_pwem_meta.%06d" %i
                            filepath = os.path.join(self.workingdir,filename)
                            if (os.path.exists(filepath) == True):
                                os.remove(filepath)
                                
                            filename = "simulation_%06d.py" %i
                            filepath = os.path.join(self.workingdir,filename)
                            if (os.path.exists(filepath) == True):
                                os.remove(filepath)
                        
                        script_path = os.path.join(self.scriptsdir,"pegasus-s3-rm.sh")
                        self.logger.info ('Calling %s...' %script_path)
                        subprocess_args = [script_path,S3_URL_PREFIX,S3_BUCKET,S3_BUCKET_KEY]
                        returncode = self.subprocess_popen(subprocess_args)
                        if returncode != 0:
                            self.logger.warning ('pegasus-s3-rm.sh returned nonzero returncode: %s' %str(returncode))
        
                        script_path = os.path.join(self.scriptsdir,"pegasus-aws-batch-delete.sh")
                        self.logger.info ('Calling %s...' %script_path)
                        subprocess_args = [script_path,self.workingdir,prefix]
                        returncode = self.subprocess_popen(subprocess_args)
                        if returncode != 0:
                            self.logger.warning ('pegasus-aws-batch-delete.sh returned nonzero exitCode: %s' %str(exitCode))

                        shutil.rmtree(submit_dir)
                        return True
                        
                    else:
                        self.logger.error ('Wrapper.py run_workflow: Pegasus submit directory %s not created' %submit_dir)
                        return False
                
                else:
                    self.logger.error ('Wrapper.py run_workflow: pegasus-aws-batch-create.sh returned nonzero returncode: %s' %str(returncode))
                    return False
                
            except PegasusClientError as e:
            
                self.logger.error ('Wrapper.py run_workflow: PegasusClientError Exception: %s\n' %str(e))
                return False
                
        except Exception as e:
            
            self.logger.error ('Wrapper.py run_workflow: Exception: %s\n' %str(e))
            return False
 
