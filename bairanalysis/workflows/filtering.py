from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.afni import TStat, Automask, Detrend, TSmooth, Calc


def make_w_smooth(roi=''):
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
    n_c.inputs.out_file = f'filtered_{roi}.nii.gz'

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
