from nipype.interfaces import matlab
from .workflows.hrf_3T import create_workflow_hrf_3T

from .utils import PROJECT_DIR

matlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")


def compute_hrf():

    s = create_workflow_hrf_3T()

    input_node = s.get_node('input')
    input_node.inputs.func = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_bold.nii'
    input_node.inputs.anat = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/anat 3T/sub-beilen_ses-UMCU3Tdaym13_acq-wholebrain_T1w.nii'
    input_node.inputs.events = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_events.tsv'

    s.base_dir = str(PROJECT_DIR / 'analysis')
    s.write_graph(graph2use='flat')

    s.run(plugin='MultiProc')
