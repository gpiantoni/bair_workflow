from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.ants import Registration, ApplyTransforms


def make_w_coreg_7T_3T(session=''):

    w = Workflow(f'coreg_7T{session}_3T')

    n_in = Node(IdentityInterface(fields=[
        'T1w_7T',
        'T1w_3T',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'mat_ants',
        'T1w_3T',
        ]), name='output')

    n_coreg = Node(Registration(), name='antsReg')
    n_coreg.inputs.use_histogram_matching = False
    n_coreg.inputs.dimension = 3
    n_coreg.inputs.winsorize_lower_quantile = 0.001
    n_coreg.inputs.winsorize_upper_quantile = 0.999
    n_coreg.inputs.float = False
    n_coreg.inputs.interpolation = 'Linear'
    n_coreg.inputs.transforms = ['Translation', 'Rigid']
    n_coreg.inputs.transform_parameters = [[0.1, ], [0.1, ]]
    n_coreg.inputs.metric = ['MI', 'MI']
    n_coreg.inputs.metric_weight = [1, 1]
    n_coreg.inputs.radius_or_number_of_bins = [32, 32]
    n_coreg.inputs.sampling_strategy = ['Regular', 'Regular']
    n_coreg.inputs.sampling_percentage = [0.25, 0.5]
    n_coreg.inputs.sigma_units = ['vox', 'mm']
    n_coreg.inputs.convergence_threshold = [1e-6, 1e-6]
    n_coreg.inputs.smoothing_sigmas = [[8, 4, 0], [1, 0]]
    n_coreg.inputs.shrink_factors = [[5, 3, 1], [1, 1]]
    n_coreg.inputs.convergence_window_size = [20, 10]
    n_coreg.inputs.number_of_iterations = [[1000, 500, 200], [250, 100]]
    n_coreg.inputs.output_warped_image = True
    n_coreg.inputs.output_inverse_warped_image = True
    n_coreg.inputs.output_transform_prefix = 'ants_3T_to_7T' + session

    n_7t23t = Node(ApplyTransforms(), name='ants_7t23t')
    n_7t23t.inputs.dimension = 3
    n_7t23t.inputs.invert_transform_flags = True
    n_7t23t.inputs.interpolation = 'Linear'

    n_3t27t = Node(ApplyTransforms(), name='ants_3t27t')
    n_3t27t.inputs.dimension = 3
    n_3t27t.inputs.interpolation = 'Linear'
    n_3t27t.inputs.default_value = 0

    w.connect(n_in, 'T1w_3T', n_coreg, 'moving_image')
    w.connect(n_in, 'T1w_7T', n_coreg, 'fixed_image')
    w.connect(n_coreg, 'forward_transforms', n_out, 'mat_ants')

    w.connect(n_coreg, 'forward_transforms', n_7t23t, 'transforms')
    w.connect(n_in, 'T1w_7T', n_7t23t, 'input_image')
    w.connect(n_in, 'T1w_3T', n_7t23t, 'reference_image')

    w.connect(n_coreg, 'forward_transforms', n_3t27t, 'transforms')
    w.connect(n_in, 'T1w_3T', n_3t27t, 'input_image')
    w.connect(n_in, 'T1w_7T', n_3t27t, 'reference_image')

    return w


def make_w_coreg_7T_7T():

    w = Workflow('coreg_7T_7T')

    n_in = Node(IdentityInterface(fields=[
        'T1w_SE',
        'T1w_GE',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'mat_ants',
        'func',
        ]), name='output')

    n_coreg = Node(Registration(), name='antsReg')
    n_coreg.inputs.dimension = 3
    n_coreg.inputs.winsorize_lower_quantile = 0.005
    n_coreg.inputs.winsorize_upper_quantile = 0.995
    n_coreg.inputs.float = True
    n_coreg.inputs.interpolation = 'Linear'
    n_coreg.inputs.transforms = ['Rigid', 'Affine']
    n_coreg.inputs.transform_parameters = [[0.2, ], [0.1, ]]
    n_coreg.inputs.metric = ['MI', 'MI']
    n_coreg.inputs.metric_weight = [1, 1]
    n_coreg.inputs.radius_or_number_of_bins = [32, 32]
    n_coreg.inputs.sampling_strategy = ['Regular', 'Regular']
    n_coreg.inputs.sampling_percentage = [0.25, 0.25]
    n_coreg.inputs.sigma_units = ['vox', 'vox']
    n_coreg.inputs.convergence_threshold = [1e-6, 1e-6]
    n_coreg.inputs.smoothing_sigmas = [[4, 2, 0], [1, 0]]
    n_coreg.inputs.shrink_factors = [[3, 2, 1], [2, 1]]
    n_coreg.inputs.convergence_window_size = [20, 10]
    n_coreg.inputs.number_of_iterations = [[1000, 500, 200], [500, 200]]
    n_coreg.inputs.restrict_deformation = [[], [1, 1, 0]]
    n_coreg.inputs.output_warped_image = True
    n_coreg.inputs.output_inverse_warped_image = True

    n_ge2se = Node(ApplyTransforms(), name='ants_ge2se')
    n_ge2se.inputs.dimension = 3
    n_ge2se.inputs.invert_transform_flags = True
    n_ge2se.inputs.interpolation = 'Linear'

    n_se2ge = Node(ApplyTransforms(), name='ants_se2ge')
    n_se2ge.inputs.dimension = 3
    n_se2ge.inputs.interpolation = 'Linear'
    n_se2ge.inputs.default_value = 0

    w.connect(n_in, 'T1w_SE', n_coreg, 'moving_image')
    w.connect(n_in, 'T1w_GE', n_coreg, 'fixed_image')
    w.connect(n_coreg, 'forward_transforms', n_out, 'mat_ants')

    w.connect(n_coreg, 'forward_transforms', n_ge2se, 'transforms')
    w.connect(n_in, 'T1w_GE', n_ge2se, 'input_image')
    w.connect(n_in, 'T1w_SE', n_ge2se, 'reference_image')

    w.connect(n_coreg, 'forward_transforms', n_se2ge, 'transforms')
    w.connect(n_in, 'T1w_SE', n_se2ge, 'input_image')
    w.connect(n_in, 'T1w_GE', n_se2ge, 'reference_image')

    return w


def make_w_coreg_7T():
    """Contains examples on how to convert from struct to func and from func to
    struct"""
    w = Workflow('coreg_7T')

    n_in = Node(IdentityInterface(fields=[
        'T1w',
        'mean',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'mat_ants',
        ]), name='output')

    n_coreg = Node(Registration(), name='antsReg')
    n_coreg.inputs.winsorize_lower_quantile = 0.005
    n_coreg.inputs.winsorize_upper_quantile = 0.995
    n_coreg.inputs.dimension = 3
    n_coreg.inputs.float = True
    n_coreg.inputs.interpolation = 'Linear'
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
    n_coreg.inputs.output_transform_prefix = 'ants_func_to_struct'

    n_s2f = Node(ApplyTransforms(), name='ants_struct2func')
    n_s2f.inputs.dimension = 3
    n_s2f.inputs.invert_transform_flags = True
    n_s2f.inputs.interpolation = 'NearestNeighbor'

    n_f2s = Node(ApplyTransforms(), name='ants_func2struct')
    n_f2s.inputs.dimension = 3
    n_f2s.inputs.interpolation = 'NearestNeighbor'
    n_f2s.inputs.default_value = 0

    w.connect(n_in, 'T1w', n_coreg, 'fixed_image')
    w.connect(n_in, 'mean', n_coreg, 'moving_image')
    w.connect(n_coreg, 'forward_transforms', n_out, 'mat_ants')

    w.connect(n_coreg, 'forward_transforms', n_s2f, 'transforms')
    w.connect(n_in, 'T1w', n_s2f, 'input_image')
    w.connect(n_in, 'mean', n_s2f, 'reference_image')

    w.connect(n_coreg, 'forward_transforms', n_f2s, 'transforms')
    w.connect(n_in, 'mean', n_f2s, 'input_image')
    w.connect(n_in, 'T1w', n_f2s, 'reference_image')

    return w
