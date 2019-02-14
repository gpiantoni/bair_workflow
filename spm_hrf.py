import nipype.interfaces.spm as spm  # spm
import nipype.interfaces.fsl as fsl  # fsl
import nipype.interfaces.matlab as mlab  # how to run matlab
import nipype.interfaces.utility as util  # utility
import nipype.pipeline.engine as pe  # pypeline engine
import nipype.algorithms.modelgen as model  # model specification


mlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")

from bair_analysis.

def create_workflow_hrf_3T():
    input_node.inputs.func =  '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_bold.nii'
    input_node.inputs.anat = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/anat 3T/sub-beilen_ses-UMCU3Tdaym13_acq-wholebrain_T1w.nii'
    input_node.inputs.events = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_events.tsv'


    preproc.run(plugin='MultiProc')
