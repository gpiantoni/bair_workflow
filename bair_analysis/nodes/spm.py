from nipype.pipeline.engine import Node
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.interfaces.spm import (
    Realign,
    Coregister,
    Level1Design,
    EstimateModel,
    EstimateContrast,
    )


# node realign
realign = Node(interface=Realign(), name="realign")
realign.inputs.register_to_mean = True

# node coregister
coreg = Node(interface=Coregister(), name='coreg')

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
