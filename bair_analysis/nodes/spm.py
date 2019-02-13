from pathlib import Path
from nipype.pipeline.engine import Node
from nipype.algorithms.modelgen import SpecifySPMModel
from nipype.interfaces.spm import (
    Realign,
    Coregister,
    Level1Design,
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
level1design.inputs.bases = {'hrf':{'derivs': [0,0]}}
