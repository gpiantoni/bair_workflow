from nipype.interfaces.afni import Allineate
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface


def make_w_coreg_3T():

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

    w = Workflow('coreg_7T')
    w.connect(n_in, 'mean', n_allineate, 'in_file')
    w.connect(n_in, 'T1w', n_allineate, 'reference')
    w.connect(n_allineate, 'out_matrix', n_out, 'mat_func2struct')

    return w
