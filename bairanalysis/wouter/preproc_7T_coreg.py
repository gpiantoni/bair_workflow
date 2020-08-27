from nipype.interfaces.afni import Allineate
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.ants import Registration

def make_w_coreg_3T_ants():
    """Contains examples on how to convert from struct to func and from func to
    struct"""
    w = Workflow('coreg_7T')

    n_in = Node(IdentityInterface(fields=[
        'T1w',
        'mean',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'mat_func2struct',
        ]), name='output')

    n_coreg = Node(Registration(), name='antsReg')
    n_coreg.inputs.winsorize_lower_quantile = 0.005
    n_coreg.inputs.winsorize_upper_quantile = 0.995
    n_coreg.inputs.dimension = 3
    n_coreg.inputs.float = True
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
    # n_coreg.inputs.restrict_deformation = [[], [1, 1, 0]]
    n_coreg.inputs.use_histogram_matching = [True, True]
    n_coreg.inputs.output_warped_image = True
    n_coreg.inputs.output_inverse_warped_image = True
    n_coreg.inputs.output_transform_prefix = 'ants_func_to_struct'
    n_coreg.inputs.interpolation = 'Linear'

    w.connect(n_in, 'T1w', n_coreg, 'fixed_image')
    w.connect(n_in, 'mean', n_coreg, 'moving_image')
    w.connect(n_coreg, 'forward_transforms', n_out, 'mat_func2struct')

    return w

def make_w_coreg_3T_afni():

    n_in = Node(IdentityInterface(fields=[
        'mean',
        'T1w',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'mat_func2struct',
        ]), name='output')

    n_allineate = Node(interface=Allineate(), name='allineate')
    n_allineate.inputs.one_pass = True
    n_allineate.inputs.args = '-master BASE'
    n_allineate.inputs.warp_type = 'shift_rotate'
    n_allineate.inputs.cost = 'nmi'
    n_allineate.inputs.outputtype = 'NIFTI'
    n_allineate.inputs.out_file = 'afni_realigned.nii.gz'
    n_allineate.inputs.out_matrix = 'afni_realigned.aff12.1D'

    w = Workflow('coreg_afni')
    w.connect(n_in, 'mean', n_allineate, 'in_file')
    w.connect(n_in, 'T1w', n_allineate, 'reference')
    w.connect(n_allineate, 'out_matrix', n_out, 'mat_func2struct')

    return w
