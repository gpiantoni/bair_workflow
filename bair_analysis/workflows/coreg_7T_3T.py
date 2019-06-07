from os import environ

from nipype.interfaces.fsl import FLIRT, ConvertXFM, Reorient2Std
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface


def make_w_coreg_7T_3T(ttype=''):
    n_in = Node(IdentityInterface(fields=[
        'T1w_7T',
        'T1w_3T',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'mat_t1w3t_to_t1w7t',
        'mat_t1w7t_to_t1w3t',
        ]), name='output')

    n_7T = Node(Reorient2Std(), '7T')
    n_3T = Node(Reorient2Std(), '3T')

    n_coarse = Node(FLIRT(), 'coarse')
    n_coarse.inputs.no_search = True
    n_coarse.inputs.schedule = environ['FSLDIR'] + '/etc/flirtsch/sch3Dtrans_3dof'
    n_coarse.inputs.dof = 6

    n_fine = Node(FLIRT(), 'fine')
    n_fine.inputs.no_search = True
    # n_fine.inputs.cost = 'normcorr'
    n_fine.inputs.dof = 7

    n_3t_7t = Node(ConvertXFM(), name='t1w3t_to_t1w7t')
    n_3t_7t.inputs.concat_xfm = True
    n_3t_7t.inputs.out_file = 'mat_t1w3t_to_t1w7t.mat'

    n_7t_3t = Node(ConvertXFM(), name='t1w7t_to_t1w3t')
    n_7t_3t.inputs.invert_xfm = True
    n_7t_3t.inputs.out_file = 'mat_t1w7t_to_t1w3t.mat'

    w = Workflow('coreg_3T_7T' + ttype)
    w.connect(n_in, 'T1w_7T', n_7T, 'in_file')
    w.connect(n_in, 'T1w_3T', n_3T, 'in_file')
    w.connect(n_7T, 'out_file', n_coarse, 'reference')
    w.connect(n_3T, 'out_file', n_coarse, 'in_file')
    w.connect(n_7T, 'out_file', n_fine, 'reference')
    w.connect(n_coarse, 'out_file', n_fine, 'in_file')
    w.connect(n_coarse, 'out_matrix_file', n_3t_7t, 'in_file')
    w.connect(n_fine, 'out_matrix_file', n_3t_7t, 'in_file2')
    w.connect(n_3t_7t, 'out_file', n_7t_3t, 'in_file')
    w.connect(n_3t_7t, 'out_file', n_out, 'mat_t1w3t_to_t1w7t')
    w.connect(n_7t_3t, 'out_file', n_out, 'mat_t1w7t_to_t1w3t')

    return w
