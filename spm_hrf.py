import nipype.interfaces.spm as spm  # spm
import nipype.interfaces.fsl as fsl  # fsl
import nipype.interfaces.matlab as mlab  # how to run matlab
import nipype.interfaces.utility as util  # utility
import nipype.pipeline.engine as pe  # pypeline engine
import nipype.algorithms.modelgen as model  # model specification


mlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")


input_node = pe.Node(util.IdentityInterface(fields=[
        'func',
        'anat',
        'events',
        ]), name='input')

input_node.inputs.func =  '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_bold.nii'
input_node.inputs.anat = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/anat 3T/sub-beilen_ses-UMCU3Tdaym13_acq-wholebrain_T1w.nii'
input_node.inputs.events = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_events.tsv'

# node skull
skull = pe.Node(interface=fsl.BET(), name="skull_stripping")

# node realign
realign = pe.Node(interface=spm.Realign(), name="realign")
realign.inputs.register_to_mean = True

# node coregister
coreg = pe.Node(interface=spm.Coregister(), name='coreg')

# node design matrix
design = pe.Node(interface=model.SpecifySPMModel(), name='design_matrix')
design.inputs.input_units = 'secs'
design.inputs.output_units = 'secs'
design.inputs.high_pass_filter_cutoff = 128.
design.inputs.time_repetition = .85

# GLM
level1design = pe.Node(interface=spm.Level1Design(), name='general_linear_model')
level1design.inputs.timing_units = 'secs'
level1design.inputs.interscan_interval = .85
level1design.inputs.bases = {'hrf':{'derivs': [0,0]}}
level1design.inputs.session_info = '/home/margriet/tools/bair_analysis/analyzed/design_matrix/result_design_matrix.pklz'


# workflow
preproc = pe.Workflow(name='preproc')
preproc.base_dir = '/home/margriet/tools/bair_analysis/analyzed'
preproc.connect(input_node, 'anat', skull, 'in_file')
preproc.connect(input_node, 'func', realign, 'in_files')
preproc.connect(realign, 'mean_image', coreg, 'source')
preproc.connect(input_node, 'anat', coreg, 'target')
preproc.connect(realign, 'realigned_files', coreg, 'apply_to_files')
preproc.connect(realign, 'realigned_files', design, 'functional_runs')
preproc.connect(input_node, 'events', design, 'bids_event_file')
preproc.connect(design, 'session_info', level1design, 'session_info')


preproc.write_graph(graph2use='flat')

preproc.run(plugin='MultiProc')
