from nipype.interfaces import matlab
from .workflows.hrf_3T import create_workflow_hrf_3T

from .utils import ANALYSIS_DIR, SUBJECTS_DIR

matlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")


def compute_hrf():

    s = create_workflow_hrf_3T()

    input_node = s.get_node('input')
    input_node.inputs.t1w = str(
        SUBJECTS_DIR
        / 'sub-beilen/ses-UMCU3Tdaym13/anat/sub-beilen_ses-UMCU3Tdaym13_acq-wholebrain_T1w.nii')
    input_node.inputs.bold = str(
        SUBJECTS_DIR
        / 'sub-beilen/ses-UMCU3Tdaym13/func/sub-beilen_ses-UMCU3Tdaym13_task-bairhrfpattern_run-1_bold.nii')
    input_node.inputs.events = str(
        SUBJECTS_DIR
        / 'sub-beilen/ses-UMCU3Tdaym13/func/sub-beilen_ses-UMCU3Tdaym13_task-bairhrfpattern_run-1_events.tsv')

    s.base_dir = str(ANALYSIS_DIR)
    s.write_graph(graph2use='flat')

    s.run(plugin='MultiProc')
