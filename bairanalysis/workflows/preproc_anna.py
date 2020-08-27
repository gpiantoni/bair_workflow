from nipype.interfaces.afni import Volreg, TStat, Automask, TCat, ClipLevel, Calc, Means
from nipype.interfaces.fsl import ExtractROI
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface


def make_w_preproc_anna():
    n_in = Node(IdentityInterface(fields=[
        'prf_run1',
        'prf_run2',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'prf_preproc',
        ]), name='output')

    n_roi = Node(ExtractROI(), name='roi')
    n_roi.inputs.t_min = 5
    n_roi.inputs.t_size = 1

    n_volreg = Node(interface=Volreg(), name='volreg')
    n_volreg.inputs.outputtype = 'NIFTI'
    n_volreg.inputs.zpad = 1
    n_volreg.inputs.oned_file = 'pRF_run1_mov.1D'

    n_volreg2 = Node(interface=Volreg(), name='volreg2')
    n_volreg2.inputs.outputtype = 'NIFTI'
    n_volreg2.inputs.zpad = 1
    n_volreg2.inputs.oned_file = 'pRF_run2_mov.1D'

    n_tcat = Node(interface=TCat(), name='tcat')
    n_tcat.inputs.outputtype = 'NIFTI'
    n_tcat.inputs.rlt = '++'
    n_tcat2 = Node(interface=TCat(), name='tcat2')
    n_tcat2.inputs.outputtype = 'NIFTI'
    n_tcat2.inputs.rlt = '++'

    n_tcat = Node(interface=TCat(), name='tcat')
    n_tcat.inputs.outputtype = 'NIFTI'
    n_tcat.inputs.rlt = '++'
    n_tcat2 = Node(interface=TCat(), name='tcat2')
    n_tcat2.inputs.outputtype = 'NIFTI'
    n_tcat2.inputs.rlt = '++'

    n_clip1 = Node(ClipLevel(), 'clip1')
    n_clip2 = Node(ClipLevel(), 'clip2')
    n_clip_both = Node(ClipLevel(), 'clip_both')

    n_mask1 = Node(Automask(), 'mask1')
    n_mask1.inputs.outputtype = 'NIFTI'
    n_mask2 = Node(Automask(), 'mask2')
    n_mask2.inputs.outputtype = 'NIFTI'
    n_mask_both = Node(Automask(), 'mask_both')
    n_mask_both.inputs.outputtype = 'NIFTI'

    n_calc1 = Node(Calc(), 'calc1')
    n_calc1.inputs.expr = 'step(a)*b'
    n_calc1.inputs.outputtype = 'NIFTI'
    n_calc2 = Node(Calc(), 'calc2')
    n_calc2.inputs.expr = 'step(a)*b'
    n_calc2.inputs.outputtype = 'NIFTI'
    n_calc_both = Node(Calc(), 'calc_both')
    n_calc_both.inputs.expr = 'step(a)*b'
    n_calc_both.inputs.outputtype = 'NIFTI'

    n_mean1 = Node(TStat(), 'mean1')
    n_mean1.inputs.outputtype = 'NIFTI'
    n_mean2 = Node(TStat(), 'mean2')
    n_mean2.inputs.outputtype = 'NIFTI'

    n_ratio1 = Node(Calc(), 'ratio1')
    n_ratio1.inputs.expr = '(a/b)'
    n_ratio1.inputs.outputtype = 'NIFTI'
    n_ratio1.inputs.args = '-fscale'

    n_means = Node(Means(), name='means')
    n_means.inputs.datum = 'float'
    n_means.inputs.outputtype = 'NIFTI'

    w = Workflow('nipype_prf')
    w.connect(n_in, 'prf_run1', n_roi, 'in_file')
    w.connect(n_in, 'prf_run1', n_volreg, 'in_file')
    w.connect(n_roi, 'roi_file', n_volreg, 'basefile')
    w.connect(n_volreg, 'out_file', n_tcat, 'in_files')
    w.connect(n_in, 'prf_run2', n_volreg2, 'in_file')
    w.connect(n_roi, 'roi_file', n_volreg2, 'basefile')
    w.connect(n_volreg2, 'out_file', n_tcat2, 'in_files')
    w.connect(n_tcat, 'out_file', n_clip1, 'in_file')
    w.connect(n_tcat2, 'out_file', n_clip2, 'in_file')
    w.connect(n_tcat, 'out_file', n_mask1, 'in_file')
    w.connect(n_clip1, ('clip_val', _to_args), n_mask1, 'args')
    w.connect(n_tcat2, 'out_file', n_mask2, 'in_file')
    w.connect(n_clip2, ('clip_val', _to_args), n_mask2, 'args')
    w.connect(n_mask1, 'out_file', n_calc1, 'in_file_a')
    w.connect(n_tcat, 'out_file', n_calc1, 'in_file_b')
    w.connect(n_mask2, 'out_file', n_calc2, 'in_file_a')
    w.connect(n_tcat2, 'out_file', n_calc2, 'in_file_b')
    w.connect(n_tcat, 'out_file', n_mean1, 'in_file')
    w.connect(n_tcat2, 'out_file', n_mean2, 'in_file')
    w.connect(n_tcat, 'out_file', n_means, 'in_file_a')
    w.connect(n_tcat2, 'out_file', n_means, 'in_file_b')
    w.connect(n_means, 'out_file', n_mask_both, 'in_file')
    w.connect(n_means, 'out_file', n_clip_both, 'in_file')
    w.connect(n_clip_both, ('clip_val', _to_args), n_mask_both, 'args')
    w.connect(n_mask_both, 'out_file', n_calc_both, 'in_file_a')
    w.connect(n_means, 'out_file', n_calc_both, 'in_file_b')
    w.connect(n_calc_both, 'out_file', n_out, 'prf_preproc')

    return w


def _to_args(si):
    return f'-SI {si}'




