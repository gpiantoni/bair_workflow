from nipype import Node, Workflow
from nipype.interfaces import matlab
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.fsl import FLIRT

from .preproc.preproc import create_workflow_preproc_spm
from .preproc.mri_realign import create_workflow_coreg_epi2t1w
from .glm.hrfpattern import (
    create_workflow_hrfpattern_spm,
    create_workflow_hrfpattern_fsl,
    )

matlab.MatlabCommand.set_default_matlab_cmd("matlab -nodesktop -nosplash")


def create_workflow_hrfpattern_7T(glm='spm'):
    input_node = Node(IdentityInterface(fields=[
        'bold',
        'events',
        't2star_fov',
        't2star_whole',
        't1w',
        ]), name='input')

    coreg_tstat = Node(interface=FLIRT(), name='realign_result_to_anat')
    coreg_tstat.inputs.apply_xfm = True

    w = Workflow('hrf_7T')

    w_preproc = create_workflow_preproc_spm()
    if glm == 'spm':
        w_hrfpattern = create_workflow_hrfpattern_spm()
    elif glm == 'fsl':
        w_hrfpattern = create_workflow_hrfpattern_fsl()
    w_coreg = create_workflow_coreg_epi2t1w()

    w.connect(input_node, 'bold', w_preproc, 'input.bold')
    w.connect(input_node, 'events', w_hrfpattern, 'input.events')
    w.connect(input_node, 't2star_fov', w_coreg, 'input.t2star_fov')
    w.connect(input_node, 't2star_whole', w_coreg, 'input.t2star_whole')
    w.connect(input_node, 't1w', w_coreg, 'input.t1w')
    w.connect(input_node, 't1w', coreg_tstat, 'reference')
    w.connect(w_preproc, 'realign.realigned_files', w_hrfpattern, 'input.bold')
    w.connect(w_preproc, 'realign.mean_image', w_coreg, 'input.bold_mean')

    w.connect(w_hrfpattern, 'output.T_image', coreg_tstat, 'in_file')
    w.connect(w_coreg, 'output.mat_epi2t1w', coreg_tstat, 'in_matrix_file')

    return w


def create_workflow_hrfpattern_3T(glm='spm'):
    input_node = Node(IdentityInterface(fields=[
        'bold',
        'events',
        ]), name='input')

    w = Workflow('hrf_3T')

    w_preproc = create_workflow_preproc_spm()
    if glm == 'spm':
        w_hrfpattern = create_workflow_hrfpattern_spm()
    elif glm == 'fsl':
        w_hrfpattern = create_workflow_hrfpattern_fsl()

    w.connect(input_node, 'bold', w_preproc, 'input.bold')
    w.connect(input_node, 'events', w_hrfpattern, 'input.events')
    w.connect(w_preproc, 'realign.realigned_files', w_hrfpattern, 'input.bold')

    return w
