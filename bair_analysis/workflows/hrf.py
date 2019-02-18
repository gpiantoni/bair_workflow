from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.interfaces.spm import (
    Level1Design,
    EstimateModel,
    EstimateContrast,
    )


def create_workflow_hrfpattern():

    input_node = Node(IdentityInterface(fields=[
        'bold',
        'events',
        ]), name='input')

    output_node = Node(IdentityInterface(fields=[
        'spmT_image',
        ]), name='output')

    # node design matrix
    design = Node(interface=SpecifySPMModel(), name='design_matrix')
    design.inputs.input_units = 'secs'
    design.inputs.output_units = 'secs'
    design.inputs.high_pass_filter_cutoff = 128.
    design.inputs.time_repetition = .85

    # GLM
    level1design = Node(interface=Level1Design(), name='general_linear_model')
    level1design.inputs.timing_units = 'secs'
    level1design.inputs.interscan_interval = .85
    level1design.inputs.bases = {'hrf': {'derivs': [0, 0]}}

    level1estimate = Node(interface=EstimateModel(), name="level1estimate")
    level1estimate.inputs.estimation_method = {'Classical': 1}

    contrastestimate = Node(interface=EstimateContrast(), name="contrastestimate")
    contrastestimate.inputs.contrasts = [
        ('Visual', 'T', ['1', ], [1, ])
        ]

    w = Workflow(name='hrfpattern')
    w.connect(input_node, 'bold', design, 'functional_runs')
    w.connect(input_node, 'events', design, 'bids_event_file')
    w.connect(design, 'session_info', level1design, 'session_info')
    w.connect(level1design, 'spm_mat_file', level1estimate, 'spm_mat_file')
    w.connect(level1estimate, 'spm_mat_file', contrastestimate, 'spm_mat_file')
    w.connect(level1estimate, 'beta_images', contrastestimate, 'beta_images')
    w.connect(level1estimate, 'residual_image', contrastestimate, 'residual_image')
    w.connect(contrastestimate, 'spmT_images', output_node, 'spmT_image')

    return w
