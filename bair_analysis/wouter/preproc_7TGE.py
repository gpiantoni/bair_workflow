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
        ]), name='output')

    n_mul = Node(interface=BinaryMaths(), name='mul')
    n_mul.inputs.operation = 'mul'

    n_volreg = Node(interface=Volreg(), name='volreg')
    n_volreg.inputs.outputtype = 'NIFTI'

    n_mean = Node(interface=TStat(), name='mean')
    n_mean.inputs.args = '-mean'
    n_mean.inputs.outputtype = 'NIFTI_GZ'

    w = Workflow(name='mc_func')
    w.connect(n_in, 'bold', n_mul, 'in_file')
    w.connect(n_in, 'mask', n_mul, 'operand_file')
    w.connect(n_mul, 'out_file', n_volreg, 'in_file')
    w.connect(n_volreg, 'out_file', n_out, 'bold')
    w.connect(n_volreg, 'out_file', n_mean, 'in_file')
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


"""
n = Node(interface=Qwarp(), name='qwarp')
# mean
n.inputs.in_file = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/sub-visual03/ses-UMCU7TGE/sub-visual03_ses-UMCU7TGE_task-bairspatialpatterns_run-02_bold/sub-visual03_ses-UMCU7TGE_acq-GE_dir-R_epi-r0.nii'
# mean
n.inputs.base_file = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/sub-visual03/ses-UMCU7TGE/sub-visual03_ses-UMCU7TGE_task-bairspatialpatterns_run-02_bold/sub-visual03_ses-UMCU7TGE_task-bairspatialpatterns_run-02_bold-mc-mean.nii'
n.inputs.outputtype = 'NIFTI'
n.inputs.plusminus = True
n.inputs.args = '-pmNAMES ap pa'

"""

"""


def merge_warp(warp0, warp1):
    return ' '.join([warp0, warp1])


f = Function(
    input_names=[
        'warp0',
        'warp1'
        ],
    output_names=[
        'nwarp',
    ],
    function=merge_warp,
    )

"""

"""
n = Node(interface=NwarpApply(), name='warpapply')
n.base_dir = B_DIR
# mean
n.inputs.in_file = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/sub-visual03/ses-UMCU7TGE/sub-visual03_ses-UMCU7TGE_task-bairspatialpatterns_run-02_bold/sub-visual03_ses-UMCU7TGE_acq-GE_dir-R_epi-r0.nii'
# mean
n.inputs.master = '/Fridge/users/giovanni/projects/margriet/analysis/preproc_wouter/sub-visual03/ses-UMCU7TGE/sub-visual03_ses-UMCU7TGE_task-bairspatialpatterns_run-02_bold/sub-visual03_ses-UMCU7TGE_task-bairspatialpatterns_run-02_bold-mc-mean.nii'
# n.inputs.outputtype = 'NIFTI'
n.inputs.warp  = ' a a'
n.interface.cmdline
"""
