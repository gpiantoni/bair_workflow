from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.fsl import MeanImage
from nipype.interfaces.ants import Registration, ApplyTransforms


def make_w_coreg_7TGE():
    """Contains examples on how to convert from struct to func and from func to
    struct"""
    w = Workflow('coreg_7TGE')

    n_in = Node(IdentityInterface(fields=[
        'T1w',
        'func',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'mat_ants',
        'func',
        ]), name='output')

    n_mean = Node(MeanImage(), name='mean')
    n_mean.dimension = 'T'

    n_coreg = Node(Registration(), name='antsReg')
    n_coreg.inputs.winsorize_lower_quantile = 0.005
    n_coreg.inputs.winsorize_upper_quantile = 0.995
    n_coreg.inputs.dimension = 3
    n_coreg.inputs.float = True
    n_coreg.inputs.interpolation = 'NearestNeighbor'
    n_coreg.inputs.transforms = ['Rigid', 'Affine']
    n_coreg.inputs.transform_parameters = [[0.1, ], [0.1, ]]
    n_coreg.inputs.metric = ['MI', 'MI']
    n_coreg.inputs.metric_weight = [1, 1]
    n_coreg.inputs.radius_or_number_of_bins = [32, 32]
    n_coreg.inputs.sampling_strategy = ['Regular', 'Regular']
    n_coreg.inputs.sampling_percentage = [0.25, 0.25]
    n_coreg.inputs.sigma_units = ['vox', 'vox']
    n_coreg.inputs.convergence_threshold = [1e-6, 1e-6]
    n_coreg.inputs.smoothing_sigmas = [[4, 2, 0], [1, 0]]
    n_coreg.inputs.shrink_factors = [[5, 3, 1], [3, 1]]
    n_coreg.inputs.convergence_window_size = [20, 10]
    n_coreg.inputs.number_of_iterations = [[1000, 500, 200], [500, 200]]
    n_coreg.inputs.restrict_deformation = [[], [1, 1, 0]]
    n_coreg.inputs.output_warped_image = True
    n_coreg.inputs.output_inverse_warped_image = True

    n_s2f = Node(ApplyTransforms(), name='ants_struct2func')
    n_s2f.inputs.dimension = 3
    n_s2f.inputs.invert_transform_flags = True
    n_s2f.inputs.interpolation = 'NearestNeighbor'

    n_f2s = Node(ApplyTransforms(), name='ants_func2struct')
    n_f2s.inputs.dimension = 3
    n_f2s.inputs.interpolation = 'NearestNeighbor'
    n_f2s.inputs.default_value = 0

    w.connect(n_in, 'func', n_mean, 'in_file')
    w.connect(n_in, 'T1w', n_coreg, 'fixed_image')
    w.connect(n_mean, 'out_file', n_coreg, 'moving_image')
    w.connect(n_coreg, 'forward_transforms', n_out, 'mat_ants')

    w.connect(n_coreg, 'forward_transforms', n_s2f, 'transforms')
    w.connect(n_in, 'T1w', n_s2f, 'input_image')
    w.connect(n_mean, 'out_file', n_s2f, 'reference_image')

    w.connect(n_coreg, 'forward_transforms', n_f2s, 'transforms')
    w.connect(n_mean, 'out_file', n_f2s, 'input_image')
    w.connect(n_in, 'T1w', n_f2s, 'reference_image')

    return w
