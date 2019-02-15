from nipype.interfaces import matlab
from bair_analysis.workflows.hrf_7T import create_workflow_hrf_7T

from bair_analysis.utils import ANALYSIS_DIR, SUBJECTS_DIR

matlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")


w = create_workflow_hrf_7T()

input_node = w.get_node('input')
input_node.inputs.t1w = str(
    SUBJECTS_DIR
    / 'sub-beilen/ses-UMCU7Tdaym13/anat/sub-beilen_ses-UMCU7Tdaym13_acq-wholebrain_T1w.nii')
input_node.inputs.bold = str(
    SUBJECTS_DIR
    / 'sub-beilen/ses-UMCU7Tdaym13/func/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_bold.nii')
input_node.inputs.events = str(
    SUBJECTS_DIR
    / 'sub-beilen/ses-UMCU7Tdaym13/func/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_events.tsv')

w.base_dir = str(ANALYSIS_DIR)
w.write_graph(graph2use='flat')

w.run(plugin='MultiProc')

