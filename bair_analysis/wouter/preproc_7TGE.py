from nipype.interfaces.afni import Volreg, TStat, Automask, Allineate, Qwarp
from nipype.interfaces.fsl import BinaryMaths
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.interfaces.afni import NwarpApply


def make_workflow(n_fmap=10):
    n_in = Node(IdentityInterface(fields=[
        'func',
        'fmap',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'func',
        ]), name='output')

    w = Workflow('preproc')

    w_mc_func = make_w_mcmean('func')
    if n_fmap == 1:  # nipype cannot handle conditional nodes
        w_mc_fmap = identify_workflow()
    else:
        w_mc_fmap = make_w_mcmean('fmap')
    w_masking = make_w_masking()
    w_warp = make_w_warp()

    n_apply = Node(interface=NwarpApply(), name='warpapply')
    n_apply.inputs.out_file = 'preprocessed.nii'

    w.connect(n_in, 'fmap', w_mc_fmap, 'input.epi')

    w.connect(w_mc_fmap, 'output.mean', w_masking, 'input.fmap')
    w.connect(n_in, 'func', w_masking, 'input.func')
    w.connect(w_masking, 'output.func', w_mc_func, 'input.epi')

    w.connect(w_masking, 'output.fmap', w_warp, 'input.fmap')
    w.connect(w_mc_func, 'output.mean', w_warp, 'input.func')
    w.connect(w_mc_func, 'output.motion_parameters', w_warp, 'input.motion_parameters')

    w.connect(w_warp, 'output.warping', n_apply, 'warp')
    w.connect(w_masking, 'output.func', n_apply, 'in_file')
    w.connect(w_mc_fmap, 'output.mean', n_apply, 'master')

    w.connect(n_apply, 'out_file', n_out, 'func')

    return w


def identify_workflow():
    n_in = Node(IdentityInterface(fields=[
        'epi',
        ]), name='input')
    n_out = Node(IdentityInterface(fields=[
        'mean',
        ]), name='output')

    w = Workflow(name='identity')
    w.connect(n_in, 'epi', n_out, 'mean')

    return w


def make_w_mcmean(data_type='func'):
    """func or fmap"""

    n_in = Node(IdentityInterface(fields=[
        'epi',
        ]), name='input')
    n_out = Node(IdentityInterface(fields=[
        'corrected',
        'mean',
        'motion_parameters',
        ]), name='output')

    n_middle = Node(
        interface=Function(
            input_names=[
                'in_file',
                ],
            output_names=[
                'args',
            ],
            function=select_middle_volume,
            ),
        name='select_middle_volume')

    n_volreg = Node(interface=Volreg(), name='volreg')
    n_volreg.inputs.outputtype = 'NIFTI'

    n_mean = Node(interface=TStat(), name='mean')
    n_mean.inputs.args = '-mean'
    n_mean.inputs.outputtype = 'NIFTI_GZ'

    w = Workflow(name='mc_' + data_type)

    w.connect(n_in, 'epi', n_middle, 'in_file')
    w.connect(n_in, 'epi', n_volreg, 'in_file')
    w.connect(n_middle, 'args', n_volreg, 'args')
    w.connect(n_volreg, 'out_file', n_out, 'bold')
    w.connect(n_volreg, 'out_file', n_mean, 'in_file')
    w.connect(n_volreg, 'oned_matrix_save', n_out, 'motion_parameters')
    w.connect(n_mean, 'out_file', n_out, 'mean')

    return w


def make_w_warp():

    n_in = Node(IdentityInterface(fields=[
        'func',
        'motion_parameters',
        'fmap',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'warping',
        ]), name='output')

    n_allineate = Node(interface=Allineate(), name='allineate')
    n_allineate.inputs.one_pass = True
    n_allineate.inputs.cost = 'hellinger'
    n_allineate.inputs.args = '-master BASE'
    n_allineate.inputs.warp_type = 'shift_rotate'
    n_allineate.inputs.outputtype = 'NIFTI'

    n_qwarp = Node(interface=Qwarp(), name='qwarp')
    n_qwarp.inputs.outputtype = 'NIFTI'
    n_qwarp.inputs.plusminus = True

    n_merge = Node(
        interface=Function(
            input_names=[
                'warp0',
                'warp1'
                ],
            output_names=[
                'nwarp',
            ],
            function=merge_warping,
            ),
        name='merge_warp')

    w = Workflow('warping')

    w.connect(n_in, 'fmap', n_allineate, 'in_file')
    w.connect(n_in, 'func', n_allineate, 'reference')

    w.connect(n_allineate, 'out_file', n_qwarp, 'in_file')
    w.connect(n_in, 'func', n_qwarp, 'base_file')

    w.connect(n_qwarp, 'base_warp', n_merge, 'warp0')
    w.connect(n_in, 'motion_parameters', n_merge, 'warp1')

    w.connect(n_merge, 'nwarp', n_out, 'warping')

    return w


def make_w_masking():

    n_in = Node(IdentityInterface(fields=[
        'func',
        'fmap',  # mean
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'func',
        'fmap',  # mean
        ]), name='output')

    n_mask_func = Node(interface=Automask(), name='mask_func')
    n_mask_func.inputs.clfrac = 0.4
    n_mask_func.inputs.dilate = 4
    n_mask_func.inputs.args = '-nbhrs 15'
    n_mask_func.inputs.outputtype = 'NIFTI'

    n_mask_fmap = n_mask_func.clone('mask_fmap')

    n_mul = Node(interface=BinaryMaths(), name='mul')
    n_mul.inputs.operation = 'mul'

    n_masking = Node(interface=BinaryMaths(), name='masking')
    n_masking.inputs.operation = 'mul'

    n_masking_fmap = Node(interface=BinaryMaths(), name='masking_fmap')
    n_masking_fmap.inputs.operation = 'mul'

    w = Workflow('masking')

    w.connect(n_in, 'func', n_mask_func, 'in_file')
    w.connect(n_in, 'fmap', n_mask_fmap, 'in_file')
    w.connect(n_mask_fmap, 'out_file', n_mul, 'in_file')
    w.connect(n_mask_func, 'out_file', n_mul, 'operand_file')
    w.connect(n_in, 'func', n_masking, 'in_file')
    w.connect(n_mul, 'out_file', n_masking, 'operand_file')
    w.connect(n_masking, 'out_file', n_out, 'func')

    w.connect(n_in, 'fmap', n_masking_fmap, 'in_file')
    w.connect(n_mul, 'out_file', n_masking_fmap, 'operand_file')

    w.connect(n_masking_fmap, 'out_file', n_out, 'fmap')

    return w


def merge_warping(warp0, warp1):
    return "'" + ' '.join([warp0, warp1]) + "'"


def select_middle_volume(in_file):
    from nibabel import load

    img = load(in_file)
    if img.ndim == 3:  # only one scan
        middle_dynamic = 0
    else:
        n_dynamics = img.shape[3]
        middle_dynamic = n_dynamics // 2

    return f'-base {middle_dynamic}'
