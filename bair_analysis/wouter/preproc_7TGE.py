from nipype.interfaces.afni import Resample, Volreg, TStat, Automask
from nipype.interfaces.fsl import BET
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface

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
    w.connect(n_mean, 'out_file', n_out, 'epi')
    w.connect(n_mean, 'out_file', n_mask, 'in_file')
    w.connect(n_mask, 'out_file', n_out, 'mask')

    return w


