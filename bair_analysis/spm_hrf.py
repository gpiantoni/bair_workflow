from nipype.interfaces import matlab
from .workflows.hrf_3T import create_preproc

from .utils import BASE_DIR

matlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")


def compute_hrf():

    preproc = create_workflow()

    input_node.inputs.func =  '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_bold.nii'
    input_node.inputs.anat = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/anat 3T/sub-beilen_ses-UMCU3Tdaym13_acq-wholebrain_T1w.nii'
    input_node.inputs.events = '/home/margriet/Desktop/data/beilen/ses-UMCU_7T_daym13/func/HRF pattern/sub-beilen_ses-UMCU7Tdaym13_task-bairhrfpattern_run-1_events.tsv'

    preproc.base_dir = str(BASE_DIR / 'analyzed')
    preproc.write_graph(graph2use='flat')

    preproc.run(plugin='MultiProc')

