from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.fsl import BinaryMaths, FLIRT
from nipype.interfaces.freesurfer import ReconAll, MRIConvert


def make_w_masking():
    w_mask = Workflow('masking')

    n_in = Node(IdentityInterface(fields=[
        'T1w',
        'subject',  # without sub-
        'freesurfer2func',
        'func',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'func',
        ]), name='output')

    n_fl = Node(FLIRT(), name='flirt')
    n_fl.inputs.output_type = 'NIFTI_GZ'
    n_fl.inputs.apply_xfm = True
    n_fl.inputs.interp = 'nearestneighbour'

    n_conv = Node(MRIConvert(), name='convert')
    n_conv.inputs.out_type = 'niigz'

    reconall = Node(ReconAll(), name='reconall')
    reconall.inputs.directive = 'all'
    reconall.inputs.subjects_dir = '/Fridge/R01_BAIR/freesurfer'

    w_mask.connect(n_in, 'T1w', reconall, 'T1_files')
    w_mask.connect(n_in, 'subject', reconall, 'subject_id')

    n_mul = Node(interface=BinaryMaths(), name='mul')
    n_mul.inputs.operation = 'mul'

    w_mask.connect(reconall, ('ribbon', select_ribbon), n_conv, 'in_file')
    w_mask.connect(n_conv, 'out_file', n_fl, 'in_file')
    w_mask.connect(n_in, 'func', n_fl, 'reference')
    w_mask.connect(n_in, 'freesurfer2func', n_fl, 'in_matrix_file')

    w_mask.connect(n_in, 'func', n_mul, 'in_file')
    w_mask.connect(n_fl, 'out_file', n_mul, 'operand_file')

    w_mask.connect(n_mul, 'out_file', n_out, 'func')

    return w_mask


def select_ribbon(x):
    return x[1]
