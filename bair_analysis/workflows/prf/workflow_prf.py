from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface, Merge
from nipype.interfaces.afni import TStat
from nipype.interfaces.fsl.maths import MathsCommand
from nipype.interfaces.ants import ApplyTransforms

from ...prf.lsq import PRF, PRF2CSV

REGIONS = ['V1', 'V2', 'V3']


def make_workflow():
    w = Workflow(f'prf_to_csv')

    n_in = Node(IdentityInterface(fields=[
        'atlas',
        'func_to_struct',
        'struct_to_freesurfer',
        'run_1',
        'run_2',
        'subject',
        'session',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'csv_file',
        ]), name='output')

    n_prf = Node(PRF(), 'prf')
    n_prf.inputs.threshold = 10

    n_mean = Node(interface=TStat(), name='mean')
    n_mean.inputs.args = '-mean'
    n_mean.inputs.outputtype = 'NIFTI_GZ'

    n_merge = Node(Merge(len(REGIONS)), 'merge')

    n_csv = {}
    w_roi = {}
    for i, r in enumerate(REGIONS):
        w_roi[r] = make_workflow_roi(r)

        n_csv[r] = Node(PRF2CSV(), 'prf2csv_' + r)
        n_csv[r].inputs.threshold = 0.5
        n_csv[r].inputs.region = r

        w.connect(n_in, 'atlas', w_roi[r], 'input.atlas')
        w.connect(n_in, 'func_to_struct', w_roi[r], 'input.func_to_struct')
        w.connect(n_in, 'struct_to_freesurfer', w_roi[r], 'input.struct_to_freesurfer')
        w.connect(n_mean, 'out_file', w_roi[r], 'input.ref')
        w.connect(n_in, 'subject', n_csv[r], 'subject')
        w.connect(n_in, 'session', n_csv[r], 'session')
        for k in ['r2', 'phi', 'rho', 'sigma', 'hrf']:
            w.connect(n_prf, k + '_file', n_csv[r], k + '_file')
        w.connect(w_roi[r], 'output.mask_file', n_csv[r], 'mask_file')
        w.connect(n_csv[r], 'csv_file', n_merge, 'in' + str(i + 1))

    w.connect(n_in, 'run_1', n_prf, 'nii1_file')
    w.connect(n_in, 'run_2', n_prf, 'nii2_file')
    w.connect(n_in, 'subject', n_prf, 'subject')
    w.connect(n_in, 'session', n_prf, 'session')
    w.connect(n_in, 'run_1', n_mean, 'in_file')
    w.connect(n_merge, 'out', n_out, 'csv_file')

    return w


def make_workflow_roi(region):
    """
    Benson_ROI_Names = {'V1', 'V2', 'V3', 'hV4', 'VO1', 'VO2', 'LO1', 'LO2', 'TO1', 'TO2', 'V3B', 'V3A'};

    Wang_ROI_Names = [
        'V1v', 'V1d', 'V2v', 'V2d', 'V3v', 'V3d', 'hV4', 'VO1', 'VO2', 'PHC1', 'PHC2',
        'TO2', 'TO1', 'LO2', 'LO1', 'V3B', 'V3A', 'IPS0', 'IPS1', 'IPS2', 'IPS3', 'IPS4' ,
        'IPS5', 'SPL1', 'FEF'];
    """

    w = Workflow(f'roi_{region}')

    n_in = Node(IdentityInterface(fields=[
        'atlas',
        'func_to_struct',
        'struct_to_freesurfer',
        'ref',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'mask_file',
        ]), name='output')

    n_m = Node(Merge(2), 'merge')

    n_v = Node(MathsCommand(), region)
    n_v.inputs.out_file = 'roi.nii.gz'
    n_v.inputs.nan2zeros = True

    if region == 'V1':
        n_v.inputs.args = '-uthr 1 -bin'
    elif region == 'V2':
        n_v.inputs.args = '-thr 2 -uthr 3 -bin'
    elif region == 'V3':
        n_v.inputs.args = '-thr 4 -uthr 5 -bin'
    else:
        raise ValueError(f'Unknown region {region}. It should be V1, V2, V3')

    at = Node(ApplyTransforms(), 'applytransform')
    at.inputs.dimension = 3
    at.inputs.output_image = 'roi_func.nii.gz'
    at.inputs.interpolation = 'Linear'
    at.inputs.default_value = 0
    at.inputs.invert_transform_flags = [True, True]

    w.connect(n_in, 'atlas', n_v, 'in_file')
    w.connect(n_v, 'out_file', at, 'input_image')
    w.connect(n_in, 'ref', at, 'reference_image')
    w.connect(n_in, 'struct_to_freesurfer', n_m, 'in1')
    w.connect(n_in, 'func_to_struct', n_m, 'in2')
    w.connect(n_m, 'out', at, 'transforms')
    w.connect(at, 'output_image', n_out, 'mask_file')

    return w
