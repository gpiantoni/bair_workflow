from nipype.interfaces.fsl import MeanImage, FLIRT, ConvertXFM
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.freesurfer import Tkregister2, ApplyVolTransform, ReconAll
from nipype.pipeline.engine import Workflow, Node


def make_w_freesurfer2func():
    n_in = Node(IdentityInterface(fields=[
        'T1w',
        'func',
        'subject',  # without sub-
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'func2struct',
        'struct2func',
        'freesurfer2func',
        'func2freesurfer',
        ]), name='output')

    reconall = Node(ReconAll(), name='reconall')
    reconall.inputs.directive = 'all'
    reconall.inputs.subjects_dir = '/Fridge/R01_BAIR/freesurfer'

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

    n_mean = Node(MeanImage(), name='mean')

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
    w.connect(n_in, 'T1w', reconall, 'T1_files')
    w.connect(n_in, 'subject', reconall, 'subject_id')
    w.connect(reconall, 'orig', n_fs2s, 'moving_image')
    w.connect(reconall, 'rawavg', n_fs2s, 'target_image')
    w.connect(n_in, 'func', n_mean, 'in_file')
    w.connect(reconall, 'brain', n_vol, 'source_file')
    w.connect(reconall, 'rawavg', n_vol, 'target_file')
    w.connect(n_mean, 'out_file', n_f2s, 'in_file')
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

    return w
