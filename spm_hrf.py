import nipype.interfaces.io as nio  # Data i/o
import nipype.interfaces.spm as spm  # spm
import nipype.interfaces.fsl as fsl  # fsl
import nipype.interfaces.matlab as mlab  # how to run matlab
import nipype.interfaces.utility as util  # utility
import nipype.pipeline.engine as pe  # pypeline engine
import nipype.algorithms.modelgen as model  # model specification
import os  # system functions
from csv import reader
from pathlib import Path


mlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")


import nipype.interfaces.spm as spm


def read_onsets(events_file):
    onsets = []
    durations = []
    with events_file.open() as f:
        f.readline()  # skip header
        for row in reader(f, delimiter='\t'):
            onsets.append(float(row[0]))
            durations.append(float(row[1]))
            
    return onsets, durations

input_node = pe.Node(util.IdentityInterface(fields=[
        'func', 
        'anat', 
        'events', 
        ]), name='input')
    
input_node.inputs.func =  '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_bold.nii'   
input_node.inputs.target = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/anat 3T/sub-beilen_ses-UMCU3Tdaym13_acq-wholebrain_T1w.nii'
    
# node realign
realign = pe.Node(interface=spm.Realign(), name="realign")
realign.inputs.register_to_mean = True

# node coregister
coreg = pe.Node(interface=spm.Coregister(), name='coreg')

# workflow
preproc = pe.Workflow(name='preproc')
preproc.base_dir = '/home/margriet/tools/bair_analysis/analyzed'
preproc.connect(input_node, 'func', realign, 'in_files')
preproc.connect(realign, 'realigned_files', coreg, 'source')
preproc.connect(input_node, 'anat', coreg, 'target')


preproc.write_graph(graph2use='flat')

preproc.run()

events_file = Path('/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_events.tsv')

onsets, durations = read_onsets(events_file)

from nipype.algorithms import modelgen
from nipype.interfaces.base import Bunch

s = pe.Node(interface=modelgen.SpecifySPMModel(), name='design_matrix')
s.inputs.input_units = 'secs'
s.inputs.output_units = 'secs'
s.inputs.high_pass_filter_cutoff = 128.
s.inputs.functional_runs = [
        '/home/margriet/tools/bair_analysis/analyzed/preproc/realign/rsub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_bold.nii', 
        ]
s.inputs.time_repetition = .85
s.inputs.bids_event_file = str(events_file)
s.base_dir = '/home/margriet/tools/bair_analysis/analyzed'
s.run()

level1design = pe.Node(interface=spm.Level1Design(), name='general_linear_model')
level1design.inputs.timing_units = 'secs'
level1design.inputs.interscan_interval = .85
level1design.inputs.bases = {'hrf':{'derivs': [0,0]}}
level1design.inputs.session_info = '/home/margriet/tools/bair_analysis/analyzed/design_matrix/result_design_matrix.pklz'

level1design.base_dir = '/home/margriet/tools/bair_analysis/analyzed'

level1design.run() 

s.run()