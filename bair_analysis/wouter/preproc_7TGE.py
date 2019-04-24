from nipype.interfaces.afni import Resample, Volreg, TStat, Automask, Allineate, Qwarp
from nipype.interfaces.fsl import BET, BinaryMaths
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.interfaces.afni import NwarpApply

t1res = 0.3

def bet_T1w():

    n_in = Node(IdentityInterface(fields=[
        'T1w',
        ]), name='input')
    n_out = Node(IdentityInterface(fields=[
        'T1w',
        ]), name='output')

    n_res = Node(interface=Resample(), name='resample')
    n_res.inputs.outputtype = 'NIFTI'
    n_res.inputs.resample_mode = 'NN'
    n_res.inputs.voxel_size = (t1res, ) * 3

    n_bet = Node(interface=BET(), name='bet')
    n_bet.inputs.frac = 0.01  # 0.0025
    n_bet.inputs.mask = True

    w = Workflow(name='bet_T1w')
    w.connect(n_in, 'T1w', n_res, 'in_file')
    w.connect(n_res, 'out_file', n_bet, 'in_file')
    w.connect(n_bet, 'out_file', n_out, 'T1w')

    return w


def volreg_topup():

    n_in = Node(IdentityInterface(fields=[
        'epi',
        ]), name='input')
    n_out = Node(IdentityInterface(fields=[
        'epi',
        'mean',
        'mask',
        ]), name='output')

    n_volreg = Node(interface=Volreg(), name='volreg')
    n_volreg.inputs.outputtype = 'NIFTI'

    n_mean = Node(interface=TStat(), name='mean')
    n_mean.inputs.args = '-mean'
    n_mean.inputs.outputtype = 'NIFTI_GZ'

    n_mask = Node(interface=Automask(), name='mask')
    n_mask.inputs.clfrac = 0.4
    n_mask.inputs.dilate = 4
    n_mask.inputs.args = '-nbhrs 15'
    n_mask.inputs.outputtype = 'NIFTI_GZ'

    w = Workflow(name='volreg_topup')

    w.connect(n_in, 'epi', n_volreg, 'in_file')
    w.connect(n_volreg, 'out_file', n_mean, 'in_file')
    w.connect(n_volreg, 'out_file', n_out, 'epi')
    w.connect(n_mean, 'out_file', n_out, 'mean')
    w.connect(n_mean, 'out_file', n_mask, 'in_file')
    w.connect(n_mask, 'out_file', n_out, 'mask')

    return w


def preproc_func():

    n_in = Node(IdentityInterface(fields=[
        'bold',
        ]), name='input')
    n_out = Node(IdentityInterface(fields=[
        'mask',
        ]), name='output')

    n_mask = Node(interface=Automask(), name='mask')
    n_mask.inputs.clfrac = 0.4
    n_mask.inputs.dilate = 4
    n_mask.inputs.args = '-nbhrs 15'
    n_mask.inputs.outputtype = 'NIFTI_GZ'

    w = Workflow(name='preproc_func')
    w.connect(n_in, 'bold', n_mask, 'in_file')
    w.connect(n_mask, 'out_file', n_out, 'mask')

    return w


def mc_func():

    n_in = Node(IdentityInterface(fields=[
        'bold',
        'mask',
        ]), name='input')
    n_out = Node(IdentityInterface(fields=[
        'bold',
        'mean',
        'motion_parameters',
        ]), name='output')

    n_mul = Node(interface=BinaryMaths(), name='mul')
    n_mul.inputs.operation = 'mul'

    n_middle = take_middle()

    n_volreg = Node(interface=Volreg(), name='volreg')
    n_volreg.inputs.outputtype = 'NIFTI'

    n_mean = Node(interface=TStat(), name='mean')
    n_mean.inputs.args = '-mean'
    n_mean.inputs.outputtype = 'NIFTI_GZ'

    w = Workflow(name='mc_func')
    w.connect(n_in, 'bold', n_mul, 'in_file')
    w.connect(n_in, 'mask', n_mul, 'operand_file')
    w.connect(n_in, 'bold', n_middle, 'in_file')
    w.connect(n_middle, 'args', n_volreg, 'args')
    w.connect(n_mul, 'out_file', n_volreg, 'in_file')
    w.connect(n_volreg, 'out_file', n_out, 'bold')
    w.connect(n_volreg, 'out_file', n_mean, 'in_file')
    w.connect(n_volreg, 'oned_matrix_save', n_out, 'motion_parameters')
    w.connect(n_mean, 'out_file', n_out, 'mean')

    return w


def allineate():
    n = Node(interface=Allineate(), name='allineate')
    n.inputs.one_pass = True
    n.inputs.cost = 'hellinger'
    n.inputs.args = '-master BASE'
    n.inputs.warp_type = 'shift_rotate'
    n.inputs.outputtype = 'NIFTI'

    return n


def qwarp():
    n = Node(interface=Qwarp(), name='qwarp')
    n.inputs.outputtype = 'NIFTI'
    n.inputs.plusminus = True
    return n


def f_merge_warp(warp0, warp1):
    return "'" + ' '.join([warp0, warp1]) + "'"


def merge():
    merge_func = Function(
        input_names=[
            'warp0',
            'warp1'
            ],
        output_names=[
            'nwarp',
        ],
        function=f_merge_warp,
        )

    n = Node(interface=merge_func, name='merge_warp')
    return n


def f_take_middle(in_file):
    from nibabel import load

    img = load(in_file)
    n_dynamics = img.shape[3]
    middle_dynamic = n_dynamics // 2

    return f'-base {middle_dynamic}'


def take_middle():
    func = Function(
        input_names=[
            'in_file',
            ],
        output_names=[
            'args',
        ],
        function=f_take_middle,
        )

    n = Node(interface=func, name='take_middle')
    return n


def warp_apply():
    n = Node(interface=NwarpApply(), name='warpapply')
    n.inputs.out_file = 'warped.nii'

    return n


def mc_mean(data_type='func'):
    """func or fmap"""

    n_in = Node(IdentityInterface(fields=[
        'epi',
        ]), name='input')
    n_out = Node(IdentityInterface(fields=[
        'corrected',
        'mean',
        'motion_parameters',
        ]), name='output')

    n_middle = take_middle()

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


def make_workflow():
    n_in = Node(IdentityInterface(fields=[
        'bold',
        'fmap',
        ]), name='input')

    # n_in.inputs.T1w = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/sub-visual03/ses-UMCU7TGE/msub-visual03_ses-UMCU7TGE_T1w/msub-visual03_ses-UMCU7TGE_T1w.nii'
    # n_in.inputs.fmap = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/sub-visual03/ses-UMCU7TGE/sub-visual03_ses-UMCU7TGE_acq-GE_dir-R_epi/sub-visual03_ses-UMCU7TGE_acq-GE_dir-R_epi.nii'
    # n_in.inputs.func = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/sub-visual03/ses-UMCU7TGE/sub-visual03_ses-UMCU7TGE_task-bairspatialpatterns_run-02_bold/sub-visual03_ses-UMCU7TGE_task-bairspatialpatterns_run-02_bold.nii'

    w = Workflow('preproc_7TGE')

    w_mc_func = mc_mean('func')
    w_mc_fmap = mc_mean('fmap')
    w_masking = make_w_masking()
    n_allineate = allineate()

    n_qwarp = qwarp()
    n_merge = merge()
    n_apply = warp_apply()

    w.connect(n_in, 'fmap', w_mc_fmap, 'input.epi')

    w.connect(w_mc_fmap, 'output.mean', w_masking, 'input.fmap')
    w.connect(n_in, 'func', w_masking, 'input.func')
    w.connect(w_masking, 'output.func', w_mc_func, 'input.epi')

    w.connect(w_masking, 'output.fmap', n_allineate, 'in_file')
    w.connect(w_mc_func, 'output.mean', n_allineate, 'reference')

    w.connect(n_allineate, 'out_file', n_qwarp, 'in_file')
    w.connect(w_mc_func, 'output.mean', n_qwarp, 'base_file')

    w.connect(n_qwarp, 'base_warp', n_merge, 'warp0')  # to check
    w.connect(w_mc_func, 'output.motion_parameters', n_merge, 'warp1')  # to check

    w.connect(n_merge, 'nwarp', n_apply, 'warp')
    w.connect(w_masking, 'output.func', n_apply, 'in_file')
    w.connect(w_mc_fmap, 'output.mean', n_apply, 'master')

    # w.write_graph(graph2use='flat')
    # w.write_graph(graph2use='colored')

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

    n_mask = Node(interface=Automask(), name='mask_fmap')
    n_mask.inputs.clfrac = 0.4
    n_mask.inputs.dilate = 4
    n_mask.inputs.args = '-nbhrs 15'
    n_mask.inputs.outputtype = 'NIFTI'

    n_mask1 = Node(interface=Automask(), name='mask_func')
    n_mask1.inputs.clfrac = 0.4
    n_mask1.inputs.dilate = 4
    n_mask1.inputs.args = '-nbhrs 15'
    n_mask1.inputs.outputtype = 'NIFTI'

    n_mul = Node(interface=BinaryMaths(), name='mul')
    n_mul.inputs.operation = 'mul'

    n_masking = Node(interface=BinaryMaths(), name='masking')
    n_masking.inputs.operation = 'mul'

    n_masking_fmap = Node(interface=BinaryMaths(), name='masking_fmap')
    n_masking_fmap.inputs.operation = 'mul'

    w = Workflow('masking')

    w.connect(n_in, 'func', n_mask1, 'in_file')
    w.connect(n_in, 'fmap', n_mask, 'in_file')
    w.connect(n_mask, 'out_file', n_mul, 'in_file')
    w.connect(n_mask1, 'out_file', n_mul, 'operand_file')
    w.connect(n_in, 'func', n_masking, 'in_file')
    w.connect(n_mul, 'out_file', n_masking, 'operand_file')
    w.connect(n_masking, 'out_file', n_out, 'func')

    w.connect(n_in, 'fmap', n_masking_fmap, 'in_file')
    w.connect(n_mul, 'out_file', n_masking_fmap, 'operand_file')

    w.connect(n_masking_fmap, 'out_file', n_out, 'fmap')

    return w
