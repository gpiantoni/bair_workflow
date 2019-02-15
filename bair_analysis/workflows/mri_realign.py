from nipype import Node, Workflow
from nipype.interfaces.utility import IdentityInterface

from ..nodes.fsl import skull, coreg_epi2fov, coreg_fov2whole, coreg_whole2t1w
from ..nodes.spm import realign


def create_workflow_realign_fov_t2star():

    input_node = Node(IdentityInterface(fields=[
        'bold',
        't2star_fov',
        't2star_whole',
        't1w',
        ]), name='input')
    # output = Node(IdentityInterface(fields=['7T_T1w_reg_affine', '7T_T1w_reg_SyN']), name='output')

    w = Workflow('coreg_epi_2_t1w')

    w.connect(input_node, 'epi', realign, 'in_files')

    w.connect(realign, 'mean_image', coreg_epi2fov, 'in_file')
    w.connect(input_node, 'T2star_fov', coreg_epi2fov, 'reference')

    w.connect(input_node, 'T2star_fov', coreg_fov2whole, 'in_file')
    w.connect(input_node, 'T2star_whole', coreg_fov2whole, 'reference')

    w.connect(input_node, 'T1w', skull, 'in_file')

    w.connect(input_node, 'T2star_whole', coreg_whole2t1w, 'epi')
    w.connect(skull, 'out_file', coreg_whole2t1w, 't1_brain')
    w.connect(input_node, 'T1w', coreg_whole2t1w, 't1_head')

    return w
