from nipype.pipeline.engine import Workflow
from nipype.interfaces.utility import IdentityInterface

from ..nodes.spm import (
    realign,
    design,
    level1design,
    level1estimate,
    contrastestimate,
    )

from nipype.pipeline.engine import Node


def create_workflow_hrf_7T():

    input_node = Node(IdentityInterface(fields=[
        'bold',
        'events',
        ]), name='input')

    preproc = Workflow(name='hrf_7T')
    preproc.connect(input_node, 'bold', realign, 'in_files')

    preproc.connect(realign, 'realigned_files', design, 'functional_runs')
    preproc.connect(input_node, 'events', design, 'bids_event_file')
    preproc.connect(design, 'session_info', level1design, 'session_info')
    preproc.connect(level1design, 'spm_mat_file', level1estimate, 'spm_mat_file')
    preproc.connect(level1estimate, 'spm_mat_file', contrastestimate, 'spm_mat_file')
    preproc.connect(level1estimate, 'beta_images', contrastestimate, 'beta_images')
    preproc.connect(level1estimate, 'residual_image', contrastestimate, 'residual_image')

    return preproc
