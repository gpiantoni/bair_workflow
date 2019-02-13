from nipype.pipeline.engine import Workflow

from ..nodes.utils import input_node
from ..nodes.fsl import skull
from ..nodes.spm import (
    realign,
    coreg,
    design,
    level1design,
    )


def create_preproc():
    preproc = Workflow(name='preproc')
    preproc.connect(input_node, 'anat', skull, 'in_file')
    preproc.connect(input_node, 'func', realign, 'in_files')
    preproc.connect(realign, 'mean_image', coreg, 'source')
    preproc.connect(input_node, 'anat', coreg, 'target')
    preproc.connect(realign, 'realigned_files', coreg, 'apply_to_files')
    preproc.connect(realign, 'realigned_files', design, 'functional_runs')
    preproc.connect(input_node, 'events', design, 'bids_event_file')
    preproc.connect(design, 'session_info', level1design, 'session_info')

    return preproc
