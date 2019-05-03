from nipype.interfaces.afni import Allineate
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.fsl import MeanImage


def make_w_coreg_3T():

    n_in = Node(IdentityInterface(fields=[
        'func',
        'T1w',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'mat_func2struct',
        ]), name='output')

    n_mean = Node(MeanImage(), name='mean')
    n_mean.dimension = 'T'

    n_allineate = Node(interface=Allineate(), name='allineate')
    n_allineate.inputs.one_pass = True
    n_allineate.inputs.args = '-master BASE'
    n_allineate.inputs.warp_type = 'shift_rotate'
    n_allineate.inputs.cost = 'nmi'
    n_allineate.inputs.outputtype = 'NIFTI'

    w = Workflow('coreg_7T')
    w.connect(n_in, 'func', n_mean, 'in_file')
    w.connect(n_mean, 'out_file', n_allineate, 'in_file')
    w.connect(n_in, 'T1w', n_allineate, 'reference')
    w.connect(n_allineate, 'out_matrix', n_out, 'mat_func2struct')

    return w
