from nipype.pipeline.engine import Workflow, Node
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


def create_workflow_spatialobject_fsl():

    replace_nan = Node(interface=MathsCommand(), name='replace_nan')
    replace_nan.inputs.nan2zeros = True

    # GLM
    design = Node(interface=fsl_design(), name='design')
    design.inputs.interscan_interval = .85
    design.inputs.bases = {'gamma': {'derivs': False}}
    design.inputs.model_serial_correlations = True
    design.inputs.contrasts = [
        ('Faces', 'T', ['FACES', 'HOUSES', 'LETTERS'], [1, 0, 0]),
        ('Houses', 'T', ['FACES', 'HOUSES', 'LETTERS'], [0, 1, 0]),
        ('Letters', 'T', ['FACES', 'HOUSES', 'LETTERS'], [0, 0, 1])
        ]
    modelgen = Node(interface=FEATModel(), name='glm')

    estimate = Node(interface=FILMGLS(), name="estimate")
    estimate.inputs.smooth_autocorr = True
    estimate.inputs.mask_size = 5
    estimate.inputs.threshold = 1000

    w = Workflow(name='spatialobject_fsl')
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
