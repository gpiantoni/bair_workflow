from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.interfaces.spm import Level1Design as spm_design
from nipype.interfaces.fsl import Level1Design as fsl_design
from nipype.interfaces.fsl import (
    FEATModel,
    FILMGLS,
    ContrastMgr,
    )
from nipype.interfaces.spm import (
    EstimateModel,
    EstimateContrast,
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


def create_workflow_hrfpattern_spm():

    # GLM
    design = Node(interface=spm_design(), name='design_glm')
    design.inputs.timing_units = 'secs'
    design.inputs.interscan_interval = .85
    design.inputs.bases = {'hrf': {'derivs': [0, 0]}}

    estimate = Node(interface=EstimateModel(), name="estimate")
    estimate.inputs.estimation_method = {'Classical': 1}

    contrastestimate = Node(interface=EstimateContrast(), name="contrast")
    contrastestimate.inputs.contrasts = [
        ('Visual', 'T', ['1', ], [1, ])
        ]

    w = Workflow(name='hrfpattern_spm')
    w.connect(input_node, 'bold', model, 'functional_runs')
    w.connect(input_node, 'events', model, 'bids_event_file')
    w.connect(model, 'session_info', design, 'session_info')
    w.connect(design, 'spm_mat_file', estimate, 'spm_mat_file')
    w.connect(estimate, 'spm_mat_file', contrastestimate, 'spm_mat_file')
    w.connect(estimate, 'beta_images', contrastestimate, 'beta_images')
    w.connect(estimate, 'residual_image', contrastestimate, 'residual_image')
    w.connect(contrastestimate, 'spmT_images', output_node, 'T_image')

    return w


def create_workflow_hrfpattern_fsl():

    # GLM
    design = Node(interface=fsl_design(), name='design')
    design.inputs.interscan_interval = .85
    design.inputs.bases = {'gamma': {'derivs': False}}
    design.inputs.model_serial_correlations = True

    modelgen = Node(interface=FEATModel(), name='glm')

    estimate = Node(interface=FILMGLS(), name="estimate")
    estimate.inputs.smooth_autocorr = True
    estimate.inputs.mask_size = 5
    estimate.inputs.threshold = 1000

    w = Workflow(name='hrfpattern_fsl')
    w.connect(input_node, 'bold', model, 'functional_runs')
    w.connect(input_node, 'events', model, 'bids_event_file')
    w.connect(model, 'session_info', design, 'session_info')
    w.connect(design, 'fsf_files', modelgen, 'fsf_file')
    w.connect(design, 'ev_files', modelgen, 'ev_files')
    w.connect(modelgen, 'design_file', estimate, 'design_file')
    w.connect(input_node, 'bold', estimate, 'in_file')
    w.connect(modelgen, 'con_file', estimate, 'tcon_file')
    w.connect(estimate, 'zstats', output_node, 'T_image')

    return w
