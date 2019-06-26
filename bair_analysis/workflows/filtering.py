from nipype.interfaces.fsl import Merge as FSLMerge
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface, Merge
from nipype.interfaces.fsl import ExtractROI
from nipype.interfaces.afni import TStat, Automask, Detrend, TSmooth, Calc

def make_w_filtering():
    n_in = Node(IdentityInterface(fields=[
        'func'
        ]), name='input')
    n_out = Node(IdentityInterface(fields=[
        'func'
        ]), name='output')

    n_roi1 = Node(ExtractROI(), 'roi1')
    n_roi1.inputs.t_min = 0
    n_roi1.inputs.roi_file = 'preprocessed_1.nii.gz'
    n_roi2 = Node(ExtractROI(), 'roi2')
    n_roi2.inputs.roi_file = 'preprocessed_2.nii.gz'

    w_smooth1 = make_smooth('1')
    w_smooth2 = make_smooth('2')

    n_mi = Node(Merge(2), 'merge_list')

    n_merge = Node(interface=FSLMerge(), name='merge')
    n_merge.inputs.dimension = 't'

    w = Workflow('filtering')
    w.connect(n_in, 'func', n_roi1, 'in_file')
    w.connect(n_in, ('func', _half_dynamics), n_roi1, 't_size')
    w.connect(n_in, 'func', n_roi2, 'in_file')
    w.connect(n_in, ('func', _half_dynamics), n_roi2, 't_min')
    w.connect(n_in, ('func', _half_dynamics), n_roi2, 't_size')
    w.connect(n_roi1, 'roi_file', w_smooth1, 'input.func')
    w.connect(n_roi2, 'roi_file', w_smooth2, 'input.func')
    w.connect(w_smooth1, 'output.func', n_mi, 'in1')
    w.connect(w_smooth2, 'output.func', n_mi, 'in2')
    w.connect(n_mi, 'out', n_merge, 'in_files')
    w.connect(n_merge, 'merged_file', n_out, 'func')

    return w


def make_smooth(roi=''):
    w = Workflow('filt' + roi)

    n_in = Node(IdentityInterface(fields=[
        'func'
        ]), name='input')
    n_out = Node(IdentityInterface(fields=[
        'func'
        ]), name='output')

    n_t = Node(TStat(), 'tstat')
    n_t.inputs.args = '-mean'
    n_t.inputs.out_file = 'mean.nii.gz'

    n_mask = Node(Automask(), 'mask')
    n_mask.inputs.args = '-eclip'
    n_mask.inputs.clfrac = 0.4
    n_mask.inputs.out_file = 'mask.nii.gz'

    n_d = Node(Detrend(), 'detrend')
    n_d.inputs.out_file = 'detrended.nii.gz'

    n_smooth = Node(TSmooth(), 'smooth')
    n_smooth.inputs.adaptive = 5
    n_smooth.inputs.out_file = 'smooth.nii.gz'

    n_c = Node(Calc(), 'calc')
    n_c.inputs.args = '-datum float'
    n_c.inputs.expr = 'step(a)*(b+c)'
    n_c.inputs.out_file = 'filtered.nii.gz'

    w.connect(n_in, 'func', n_t, 'in_file')
    w.connect(n_t, 'out_file', n_mask, 'in_file')
    w.connect(n_in, 'func', n_d, 'in_file')
    w.connect(n_in, ('func', afni_expr), n_d, 'args')
    w.connect(n_d, 'out_file', n_smooth, 'in_file')
    w.connect(n_mask, 'out_file', n_c, 'in_file_a')
    w.connect(n_t, 'out_file', n_c, 'in_file_b')
    w.connect(n_smooth, 'out_file', n_c, 'in_file_c')
    w.connect(n_c, 'out_file', n_out, 'func')

    return w


def _half_dynamics(in_file):
    from nibabel import load

    nii = load(in_file)
    return nii.shape[3] // 2


def afni_expr(in_file):
    from nibabel import load

    nii = load(in_file)
    n_dyn = nii.shape[3]
    return f"-expr 'cos(1*PI*t/{n_dyn})' -expr 'sin(1*PI*t/{n_dyn})' -polort 2"
