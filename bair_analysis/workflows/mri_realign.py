from nipype import Node, Workflow
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.fsl import ConvertXFM

from ..nodes.fsl import skull, coreg_epi2fov, coreg_fov2whole, coreg_whole2t1w
from ..nodes.spm import realign


def create_workflow_coreg_epi2t1w():

    input_node = Node(IdentityInterface(fields=[
        'bold',
        't2star_fov',
        't2star_whole',
        't1w',
        ]), name='input')
    output = Node(IdentityInterface(fields=[
        'mat_epi2t1w',
        ]), name='output')

    concat_fov2t1w = Node(interface=ConvertXFM(), name='mat_fov2t1w')
    concat_fov2t1w.concat_xfm = True
    concat_epi2t1w = Node(interface=ConvertXFM(), name='mat_epi2t1w')
    concat_epi2t1w.concat_xfm = True

    w = Workflow('coreg_epi2t1w')

    w.connect(input_node, 'epi', realign, 'in_files')

    w.connect(realign, 'mean_image', coreg_epi2fov, 'in_file')
    w.connect(input_node, 'T2star_fov', coreg_epi2fov, 'reference')

    w.connect(input_node, 'T2star_fov', coreg_fov2whole, 'in_file')
    w.connect(input_node, 'T2star_whole', coreg_fov2whole, 'reference')

    w.connect(input_node, 'T1w', skull, 'in_file')

    w.connect(input_node, 'T2star_whole', coreg_whole2t1w, 'epi')
    w.connect(skull, 'out_file', coreg_whole2t1w, 't1_brain')
    w.connect(input_node, 'T1w', coreg_whole2t1w, 't1_head')

    w.connect(coreg_fov2whole, 'out_matrix_file', concat_fov2t1w, 'in_file')
    w.connect(coreg_whole2t1w, 'epi2str_mat', concat_fov2t1w, 'in_file2')

    w.connect(coreg_epi2fov, 'out_matrix_file', concat_epi2t1w, 'in_file')
    w.connect(concat_fov2t1w, 'out_file', concat_epi2t1w, 'in_file2')

    w.connect(concat_epi2t1w, 'out_file', output, 'mat_epi2t1w')

    return w
