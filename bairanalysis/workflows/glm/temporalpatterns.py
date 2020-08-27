from nipype.pipeline.engine import Node, Workflow
from nipype.interfaces.utility import IdentityInterface
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.interfaces.fsl import Level1Design as fsl_design
from nipype.interfaces.fsl.maths import MathsCommand
from nipype.interfaces.fsl import (
    FEATModel,
    FILMGLS,
    )

input_node = Node(IdentityInterface(fields=[
    'bold',
    'events',
    ]), name='input')

output_node = Node(IdentityInterface(fields=[
    'T_image',
    ]), name='output')


# node design matrix
model = Node(interface=SpecifySPMModel(), name='design_matrix')
model.inputs.input_units = 'secs'
model.inputs.output_units = 'secs'
model.inputs.high_pass_filter_cutoff = 128.
model.inputs.time_repetition = .85
model.inputs.bids_condition_column = 'trial_name'


def create_workflow_temporalpatterns_fsl():

    replace_nan = Node(interface=MathsCommand(), name='replace_nan')
    replace_nan.inputs.nan2zeros = True

    # GLM
    design = Node(interface=fsl_design(), name='design')
    design.inputs.interscan_interval = .85
    design.inputs.bases = {'gamma': {'derivs': False}}
    design.inputs.model_serial_correlations = True
    design.inputs.contrasts = [
        (
            'OnePulse',
            'T',
            [
                'ONEPULSE-1',
                'ONEPULSE-2',
                'ONEPULSE-3',
                'ONEPULSE-4',
                'ONEPULSE-5',
                'ONEPULSE-6',
            ],
            [1, 1, 1, 1, 1, 1],
        ),
        (
            'TwoPulses',
            'T',
            [
                'TWOPULSE-1',
                'TWOPULSE-2',
                'TWOPULSE-3',
                'TWOPULSE-4',
                'TWOPULSE-5',
                'TWOPULSE-6',
            ],
            [1, 1, 1, 1, 1, 1],
        ),
        (
            'OnePulse_linear',
            'T',
            [
                'ONEPULSE-1',
                'ONEPULSE-2',
                'ONEPULSE-3',
                'ONEPULSE-4',
                'ONEPULSE-5',
                'ONEPULSE-6',
            ],
            [-3, -2, -1, 1, 2, 3],
        ),
        (
            'TwoPulse_linear',
            'T',
            [
                'TWOPULSE-1',
                'TWOPULSE-2',
                'TWOPULSE-3',
                'TWOPULSE-4',
                'TWOPULSE-5',
                'TWOPULSE-6',
            ],
            [-3, -2, -1, 1, 2, 3],
        ),
        ]
    modelgen = Node(interface=FEATModel(), name='glm')

    estimate = Node(interface=FILMGLS(), name="estimate")
    estimate.inputs.smooth_autocorr = True
    estimate.inputs.mask_size = 5
    estimate.inputs.threshold = 1000

    w = Workflow(name='temporalpattern_fsl')
    w.connect(input_node, 'bold', replace_nan, 'in_file')
    w.connect(replace_nan, 'out_file', model, 'functional_runs')
    w.connect(input_node, 'events', model, 'bids_event_file')
    w.connect(model, 'session_info', design, 'session_info')
    w.connect(design, 'fsf_files', modelgen, 'fsf_file')
    w.connect(design, 'ev_files', modelgen, 'ev_files')
    w.connect(modelgen, 'design_file', estimate, 'design_file')
    w.connect(replace_nan, 'out_file', estimate, 'in_file')
    w.connect(modelgen, 'con_file', estimate, 'tcon_file')
    w.connect(estimate, 'zstats', output_node, 'T_image')

    return w
