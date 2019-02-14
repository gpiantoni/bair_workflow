from nipype.pipeline.engine import Workflow
from nipype.interfaces.utility import IdentityInterface

from ..nodes.fsl import skull
from ..nodes.spm import (
    realign,
    coreg,
    design,
    level1design,
    level1estimate,
    contrastestimate,
    )

from nipype.pipeline.engine import Node


def create_workflow_hrf_3T():

    input_node = Node(IdentityInterface(fields=[
        'bold',
        't1w',
        'events',
        ]), name='input')

    preproc = Workflow(name='preproc')
    preproc.connect(input_node, 't1w', skull, 'in_file')
    preproc.connect(input_node, 'bold', realign, 'in_files')
    preproc.connect(input_node, 't1w', coreg, 'source')
    preproc.connect(realign, 'mean_image', coreg, 'target')
    preproc.connect(realign, 'realigned_files', coreg, 'apply_to_files')

    preproc.connect(coreg, 'coregistered_files', design, 'functional_runs')
    preproc.connect(input_node, 'events', design, 'bids_event_file')
    preproc.connect(design, 'session_info', level1design, 'session_info')
    preproc.connect(level1design, 'spm_mat_file', level1estimate, 'spm_mat_file')
    preproc.connect(level1estimate, 'spm_mat_file', contrastestimate, 'spm_mat_file')
    preproc.connect(level1estimate, 'beta_images', contrastestimate, 'beta_images')
    preproc.connect(level1estimate, 'residual_image', contrastestimate, 'residual_image')

    return preproc
