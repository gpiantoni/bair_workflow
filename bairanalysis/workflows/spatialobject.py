from nipype import MapNode, Node, Workflow
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.fsl import FLIRT

from .preproc.preproc import create_workflow_preproc_spm
from .preproc.mri_realign import create_workflow_coreg_epi2t1w
from .glm.spatialobject import (
    create_workflow_spatialobject_fsl,
    )


def create_workflow_spatialobject_7T():
    input_node = Node(IdentityInterface(fields=[
        'bold',
        'events',
        't2star_fov',
        't2star_whole',
        't1w',
        ]), name='input')

    coreg_tstat = MapNode(
        interface=FLIRT(), name='realign_result_to_anat',
        iterfield=['in_file', ])
    coreg_tstat.inputs.apply_xfm = True

    w = Workflow('spatialobject_7T')

    w_preproc = create_workflow_preproc_spm()
    w_spatialobject = create_workflow_spatialobject_fsl()
    w_coreg = create_workflow_coreg_epi2t1w()

    w.connect(input_node, 'bold', w_preproc, 'input.bold')
    w.connect(input_node, 'events', w_spatialobject, 'input.events')
    w.connect(input_node, 't2star_fov', w_coreg, 'input.t2star_fov')
    w.connect(input_node, 't2star_whole', w_coreg, 'input.t2star_whole')
    w.connect(input_node, 't1w', w_coreg, 'input.t1w')
    w.connect(input_node, 't1w', coreg_tstat, 'reference')
    w.connect(w_preproc, 'realign.realigned_files', w_spatialobject, 'input.bold')
    w.connect(w_preproc, 'realign.mean_image', w_coreg, 'input.bold_mean')

    w.connect(w_spatialobject, 'output.T_image', coreg_tstat, 'in_file')
    w.connect(w_coreg, 'output.mat_epi2t1w', coreg_tstat, 'in_matrix_file')

    return w
