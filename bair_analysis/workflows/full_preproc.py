from nipype.interfaces.fsl import Merge
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.matlab import MatlabCommand
from bair_analysis.wouter.preproc_7TGE import make_workflow
from bair_analysis.workflows.freesurfer2func import make_w_freesurfer2func
from bair_analysis.workflows.coreg_7TGE import make_w_coreg_7T, make_w_coreg_7T_7T
from bair_analysis.workflows.coreg_7T_3T import make_w_coreg_7T_3T
from bair_analysis.wouter.preproc_7T_coreg import make_w_coreg_3T
from nibabel import load

MatlabCommand.set_default_paths('/home/giovanni/tools/spm12')


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

    w_7TGE = make_full_workflow('7TGE', _n_dynamics(n_in.inputs.fmap_7TGE))
    w_7TSE = make_full_workflow('7TSE', _n_dynamics(n_in.inputs.fmap_7TSE))
    w_3TMB = make_full_workflow('3TMB', _n_dynamics(n_in.inputs.fmap_3TMB))
    w_coreg_7T_7T = make_w_coreg_7T_7T()
    w_coreg_3T_7TGE = make_w_coreg_7T_3T('GE')
    w_coreg_3T_7TSE = make_w_coreg_7T_3T('SE')

    w.connect(n_in, 'T1w_7TGE', w_7TGE, 'input.T1w')
    w.connect(n_in, 'func_7TGE', w_7TGE, 'input.func')
    w.connect(n_in, 'fmap_7TGE', w_7TGE, 'input.fmap')
    w.connect(n_in, 'T1w_7TSE', w_7TSE, 'input.T1w')
    w.connect(n_in, 'func_7TSE', w_7TSE, 'input.func')
    w.connect(n_in, 'fmap_7TSE', w_7TSE, 'input.fmap')
    w.connect(n_in, 'T1w_3TMB', w_3TMB, 'input.T1w')
    w.connect(n_in, 'func_3TMB', w_3TMB, 'input.func')
    w.connect(n_in, 'fmap_3TMB', w_3TMB, 'input.fmap')
    w.connect(n_in, 'subject', w_3TMB, 'input.subject')
    w.connect(n_in, 'T1w_7TGE', w_coreg_7T_7T, 'input.T1w_GE')
    w.connect(n_in, 'T1w_7TSE', w_coreg_7T_7T, 'input.T1w_SE')

    w.connect(n_in, 'T1w_3TMB', w_coreg_3T_7TGE, 'input.T1w_3T')
    w.connect(n_in, 'T1w_7TGE', w_coreg_3T_7TGE, 'input.T1w_7T')
    w.connect(n_in, 'T1w_3TMB', w_coreg_3T_7TSE, 'input.T1w_3T')
    w.connect(n_in, 'T1w_7TSE', w_coreg_3T_7TSE, 'input.T1w_7T')

    return w


def make_full_workflow(session='7TGE', n_fmap=10):
    n_in = Node(IdentityInterface(fields=[
        'T1w',
        'func',
        'fmap',
        'subject',
        ]), name='input')

    n_merge = Node(interface=Merge(), name='merge')
    n_merge.inputs.dimension = 't'

    w_preproc = make_workflow(n_fmap)

    w = Workflow(session)

    w.connect(n_in, 'func', n_merge, 'in_files')
    w.connect(n_merge, 'merged_file', w_preproc, 'input.func')
    w.connect(n_in, 'fmap', w_preproc, 'input.fmap')

    if session.startswith('7T'):
        w_coreg_7T = make_w_coreg_7T()
        w.connect(n_in, 'T1w', w_coreg_7T, 'input.T1w')
        w.connect(w_preproc, 'output.func', w_coreg_7T, 'input.func')

    else:
        w_coreg = make_w_freesurfer2func()
        w_coreg_3T = make_w_coreg_3T()

        w.connect(n_in, 'T1w', w_coreg, 'input.T1w')
        w.connect(n_in, 'subject', w_coreg, 'input.subject')
        w.connect(w_preproc, 'output.func', w_coreg, 'input.func')

        w.connect(n_in, 'T1w', w_coreg_3T, 'input.T1w')
        w.connect(w_preproc, 'output.func', w_coreg_3T, 'input.func')

    return w

def _n_dynamics(in_file):
    nii = load(in_file)
    if nii.ndim == 3:
        return 1
    else:
        return nii.shape[3]
