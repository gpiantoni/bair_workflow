from nipype.interfaces.fsl import FLIRT, ConvertXFM
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.freesurfer import Tkregister2, ApplyVolTransform
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.io import FreeSurferSource


def make_w_freesurfer2func():
    n_in = Node(IdentityInterface(fields=[
        'T1w',
        'mean',
        'subject',  # without sub-
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'brain',
        'func2struct',
        'struct2func',
        'freesurfer2func',
        'func2freesurfer',
        ]), name='output')

    freesurfer = Node(FreeSurferSource(), name='freesurfer')
    freesurfer.inputs.subjects_dir = '/Fridge/R01_BAIR/freesurfer'

    n_fs2s = Node(Tkregister2(), name='freesurfer2struct')
    n_fs2s.inputs.reg_header = True
    n_fs2s.inputs.fsl_out = 'mat_freesurfer2struct.mat'
    n_fs2s.inputs.noedit = True

    n_s2fs = Node(ConvertXFM(), name='struct2freesurfer')
    n_s2fs.inputs.invert_xfm = True
    n_s2fs.inputs.out_file = 'mat_struct2freesurfer.mat'

    n_vol = Node(ApplyVolTransform(), name='vol2vol')
    n_vol.inputs.reg_header = True
    n_vol.inputs.transformed_file = 'brain.nii.gz'

    n_f2s = Node(FLIRT(), name='func2struct')
    n_f2s.inputs.cost = 'corratio'
    n_f2s.inputs.dof = 6
    n_f2s.inputs.no_search = True
    n_f2s.inputs.output_type = 'NIFTI_GZ'
    n_f2s.inputs.out_matrix_file = 'mat_func2struct.mat'

    n_s2f = Node(ConvertXFM(), name='struct2func')
    n_s2f.inputs.invert_xfm = True
    n_s2f.inputs.out_file = 'mat_struct2func.mat'

    n_f2fs = Node(ConvertXFM(), name='func2freesurfer')
    n_f2fs.inputs.concat_xfm = True
    n_f2fs.inputs.out_file = 'mat_func2freesurfer.mat'

    n_fs2f = Node(ConvertXFM(), name='freesurfer2func')
    n_fs2f.inputs.invert_xfm = True
    n_fs2f.inputs.out_file = 'mat_freesurfer2func.mat'

    w = Workflow('coreg_3T_fs')
    w.connect(n_in, 'subject', freesurfer, 'subject_id')
    w.connect(freesurfer, 'orig', n_fs2s, 'moving_image')
    w.connect(freesurfer, 'rawavg', n_fs2s, 'target_image')
    w.connect(freesurfer, 'brain', n_vol, 'source_file')
    w.connect(freesurfer, 'rawavg', n_vol, 'target_file')
    w.connect(n_in, 'mean', n_f2s, 'in_file')
    w.connect(n_vol, 'transformed_file', n_f2s, 'reference')
    w.connect(n_f2s, 'out_matrix_file', n_s2f, 'in_file')
    w.connect(n_fs2s, 'fsl_file', n_s2fs, 'in_file')
    w.connect(n_f2s, 'out_matrix_file', n_f2fs, 'in_file')
    w.connect(n_s2fs, 'out_file', n_f2fs, 'in_file2')
    w.connect(n_f2fs, 'out_file', n_fs2f, 'in_file')
    w.connect(n_f2s, 'out_matrix_file', n_out, 'func2struct')
    w.connect(n_s2f, 'out_file', n_out, 'struct2func')
    w.connect(n_fs2f, 'out_file', n_out, 'freesurfer2func')
    w.connect(n_f2fs, 'out_file', n_out, 'func2freesurfer')
    w.connect(freesurfer, 'brain', n_out, 'brain')

    return w
