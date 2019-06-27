from nipype.interfaces.fsl import Merge
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.matlab import MatlabCommand
from nipype.interfaces.io import DataSink
from bair_analysis.wouter.preproc_7TGE import make_workflow
from bair_analysis.workflows.freesurfer2func import make_w_freesurfer2func
from bair_analysis.workflows.filtering import make_w_smooth
from bair_analysis.workflows.coreg_7TGE import make_w_coreg_7T, make_w_coreg_7T_7T
from bair_analysis.wouter.preproc_7T_coreg import make_w_coreg_3T_ants
from nibabel import load

MatlabCommand.set_default_paths('/home/giovanni/tools/spm12')

TECHNIQUES = ['3TMB', '7TGE', '7TSE']


def make_w_full_preproc(SUBJECT):

    w = Workflow('full_' + SUBJECT)

    n_in = Node(IdentityInterface(fields=[
        'T1w_7TGE',
        'func_7TGE',
        'fmap_7TGE',
        'T1w_7TSE',
        'func_7TSE',
        'fmap_7TSE',
        'T1w_3TMB',
        'func_3TMB',
        'fmap_3TMB',
        'subject',
        ]), name='input')

    n_in.inputs.subject = SUBJECT

    n_in.inputs.T1w_3TMB = f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU3TMB/anat/sub-{SUBJECT}_ses-UMCU3TMB_T1w.nii.gz'

    n_in.inputs.fmap_3TMB = f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU3TMB/fmap/sub-{SUBJECT}_ses-UMCU3TMB_acq-GE_dir-R_epi.nii.gz'
    n_in.inputs.func_3TMB = [
        f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU3TMB/func/sub-{SUBJECT}_ses-UMCU3TMB_task-bairprf_run-01_bold.nii.gz',
        f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU3TMB/func/sub-{SUBJECT}_ses-UMCU3TMB_task-bairprf_run-02_bold.nii.gz'
        ]

    n_in.inputs.T1w_7TGE = f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU7TGE/anat/sub-{SUBJECT}_ses-UMCU7TGE_T1w.nii.gz'
    n_in.inputs.fmap_7TGE = f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU7TGE/fmap/sub-{SUBJECT}_ses-UMCU7TGE_acq-GE_dir-R_epi.nii.gz'
    n_in.inputs.func_7TGE = [
        f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU7TGE/func/sub-{SUBJECT}_ses-UMCU7TGE_task-bairprf_run-01_bold.nii.gz',
        f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU7TGE/func/sub-{SUBJECT}_ses-UMCU7TGE_task-bairprf_run-02_bold.nii.gz'
        ]

    n_in.inputs.T1w_7TSE = f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU7TSE/anat/sub-{SUBJECT}_ses-UMCU7TSE_T1w.nii.gz'
    n_in.inputs.fmap_7TSE = f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU7TSE/fmap/sub-{SUBJECT}_ses-UMCU7TSE_acq-SE_dir-R_epi.nii.gz'
    n_in.inputs.func_7TSE = [
        f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU7TSE/func/sub-{SUBJECT}_ses-UMCU7TSE_task-bairprf_run-01_bold.nii.gz',
        f'/Fridge/R01_BAIR/visual_fmri/data/bids/sub-{SUBJECT}/ses-UMCU7TSE/func/sub-{SUBJECT}_ses-UMCU7TSE_task-bairprf_run-02_bold.nii.gz'
        ]

    w_pr = {
        '7TGE': make_full_workflow('7TGE', _n_dynamics(n_in.inputs.fmap_7TGE)),
        '7TSE': make_full_workflow('7TSE', _n_dynamics(n_in.inputs.fmap_7TSE)),
        '3TMB': make_full_workflow('3TMB', _n_dynamics(n_in.inputs.fmap_3TMB)),
        }
    w_coreg_7T_7T = make_w_coreg_7T_7T()

    for t in TECHNIQUES:
        w.connect(n_in, 'T1w_' + t, w_pr[t], 'input.T1w')
        w.connect(n_in, 'func_' + t, w_pr[t], 'input.func')
        w.connect(n_in, 'fmap_' + t, w_pr[t], 'input.fmap')
    w.connect(n_in, 'subject', w_pr['3TMB'], 'input.subject')

    w.connect(n_in, 'T1w_7TGE', w_coreg_7T_7T, 'input.T1w_GE')
    w.connect(n_in, 'T1w_7TSE', w_coreg_7T_7T, 'input.T1w_SE')

    n_sink = Node(DataSink(), 'sink')
    n_sink.inputs.base_directory = '/Fridge/users/giovanni/projects/margriet/analysis/output'
    n_sink.inputs.remove_dest_dir = True
    n_sink.inputs.regexp_substitutions = [
        (r'sub-visual\d{2}_ses-UMCU\d\w{3}_', ''),
        ('0GenericAffine', ''),
        ]
    w.connect(n_in, 'subject', n_sink, 'container')
    w.connect(n_in, 'T1w_3TMB', n_sink, '3TMB.@t1w')
    w.connect(n_in, 'T1w_7TGE', n_sink, '7TGE.@t1w')
    w.connect(n_in, 'T1w_7TSE', n_sink, '7TSE.@t1w')

    for t in TECHNIQUES:
        w.connect(w_pr[t], 'output.mat_func2struct', n_sink, t + '.@mat_func2struct')
        for s in ('1', '2'):
            for f in ('func', 'filtered'):
                w.connect(w_pr[t], f'output.{f}{s}', n_sink, f'{t}.@{f}{s}')

    return w


def make_full_workflow(session='7TGE', n_fmap=10):
    n_in = Node(IdentityInterface(fields=[
        'T1w',
        'func',
        'fmap',
        'subject',
        ]), name='input')

    n_out = Node(IdentityInterface(fields=[
        'func1',
        'func2',
        'filtered1',
        'filtered2',
        'mat_func2struct',
        ]), name='output')

    n_merge = Node(interface=Merge(), name='merge')
    n_merge.inputs.dimension = 't'

    w_preproc = make_workflow(n_fmap)

    w_smooth1 = make_w_smooth('1')
    w_smooth2 = make_w_smooth('2')

    w = Workflow(session)

    w.connect(n_in, 'func', n_merge, 'in_files')
    w.connect(n_merge, 'merged_file', w_preproc, 'input.func')
    w.connect(n_in, 'fmap', w_preproc, 'input.fmap')
    w.connect(w_preproc, 'output.func1', n_out, 'func1')
    w.connect(w_preproc, 'output.func2', n_out, 'func2')
    w.connect(w_preproc, 'output.func1', w_smooth1, 'input.func')
    w.connect(w_preproc, 'output.func2', w_smooth2, 'input.func')
    w.connect(w_smooth1, 'output.func', n_out, 'filtered1')
    w.connect(w_smooth2, 'output.func', n_out, 'filtered2')

    if session.startswith('7T'):
        w_coreg_7T = make_w_coreg_7T()
        w.connect(n_in, 'T1w', w_coreg_7T, 'input.T1w')
        w.connect(w_preproc, 'output.mean', w_coreg_7T, 'input.mean')
        w.connect(w_coreg_7T, 'output.mat_ants', n_out, 'mat_func2struct')

    else:
        w_coreg = make_w_freesurfer2func()
        w_coreg_3T = make_w_coreg_3T_ants()

        w.connect(n_in, 'T1w', w_coreg, 'input.T1w')
        w.connect(n_in, 'subject', w_coreg, 'input.subject')
        w.connect(w_preproc, 'output.mean', w_coreg, 'input.mean')

        w.connect(w_coreg, 'output.brain', w_coreg_3T, 'input.T1w')
        w.connect(w_preproc, 'output.mean', w_coreg_3T, 'input.mean')
        w.connect(w_coreg_3T, 'output.mat_func2struct', n_out, 'mat_func2struct')

    return w


def _n_dynamics(in_file):
    nii = load(in_file)
    if nii.ndim == 3:
        return 1
    else:
        return nii.shape[3]
