from nipype.interfaces.afni import Resample
from nipype.interfaces.fsl import BET
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface

t1res = 0.3

def preproc_7T():

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

    w = Workflow(name='preproc_spm')
    w.connect(n_in, 'T1w', n_res, 'in_file')
    w.connect(n_res, 'out_file', n_bet, 'in_file')
    w.connect(n_bet, 'out_file', n_out, 'T1w')

    return w
