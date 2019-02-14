from nipype.pipeline.engine import Workflow
from nipype.interfaces.utility import IdentityInterface

from ..nodes.fsl import skull
from ..nodes.spm import (
    realign,
    coreg,
    design,
    level1design,
    )

from nipype.pipeline.engine import Node


def create_preproc():

    input_node = Node(IdentityInterface(fields=[
        'bold',
        't1w',
        'events',
        ]), name='input')

    preproc = Workflow(name='preproc')
    preproc.connect(input_node, 't1w', skull, 'in_file')
    preproc.connect(input_node, 'bold', realign, 'in_files')
    preproc.connect(realign, 'mean_image', coreg, 'source')
    preproc.connect(input_node, 't1w', coreg, 'target')
    preproc.connect(realign, 'realigned_files', coreg, 'apply_to_files')
    preproc.connect(realign, 'realigned_files', design, 'functional_runs')
    preproc.connect(input_node, 'events', design, 'bids_event_file')
    preproc.connect(design, 'session_info', level1design, 'session_info')

    return preproc
