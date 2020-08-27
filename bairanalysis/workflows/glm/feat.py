"""Compute FSL Feat analysis

TODO
----
  - compute GLM
"""

from nipype import Workflow, Node
from nipype.interfaces.fsl import (
    Level1Design,
    FEATModel,
    FILMGLS,
    )
from nipype.algorithms.modelgen import SpecifyModel
from nipype.interfaces.utility import IdentityInterface


def mk_workflow_glm_feat():
    """Workflow to compute GLM in FSL

    TODO
    ----
    read events and create contrasts
    """
    input_node = Node(IdentityInterface(fields=[
        'bold',
        'events',
        'TR',
        ]), name='input')

    output_node = Node(IdentityInterface(fields=[
        'zmap',
        ]), name='output')

    model = Node(interface=SpecifyModel(), name='design_matrix')
    model.inputs.bids_condition_column = 'trial_name'
    model.inputs.input_units = 'secs'
    model.inputs.high_pass_filter_cutoff = 128.
    model.inputs.parameter_source = 'FSL'

    design = Node(interface=Level1Design(), name='design')
    design.inputs.bases = {'dgamma': {'derivs': True}}
    design.inputs.model_serial_correlations = True
    design.inputs.contrasts = [  # add temporal derivative with XXXTD
        (
            'gestures',
            'T',
            ['D', 'F', 'V', 'Y'],
            [1, 1, 1, 1],
        ),
        ]
    modelgen = Node(interface=FEATModel(), name='glm')

    estimate = Node(interface=FILMGLS(), name="estimate")
    estimate.inputs.smooth_autocorr = True
    estimate.inputs.mask_size = 5
    estimate.inputs.threshold = 1000

    w = Workflow('glm_feat')
    w.connect([(
        input_node, model, [
            ('bold', 'functional_runs'),
            ('events', 'bids_event_file'),
            ('TR', 'time_repetition'),
        ]), (
        input_node, design, [
            ('TR', 'interscan_interval'),
        ]), (
        model, design, [
            ('session_info', 'session_info'),
        ]), (
        design, modelgen, [
            ('fsf_files', 'fsf_file'),
            ('ev_files', 'ev_files'),
        ]), (
        modelgen, estimate, [
            ('design_file', 'design_file'),
            ('con_file', 'tcon_file'),
        ]), (
        input_node, estimate, [
            ('bold', 'in_file'),
        ]), (
        estimate, output_node, [
            ('zstats', 'zmap'),
        ])
    ])

    return w
