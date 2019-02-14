from nipype import Node, Workflow
from nipype.interfaces.utility import IdentityInterface


def create_workflow_realign_fov_t2star():

    input_node = Node(IdentityInterface(fields=[
        'bold',
        't2star_fov',
        't2star_whole',
        't1w',
        ]), name='input')
    # output = Node(IdentityInterface(fields=['7T_T1w_reg_affine', '7T_T1w_reg_SyN']), name='output')

    w = Workflow('realign_7T_to_epi')

    # it's necessary to convert to AFNI for nipype, otherwise afni/preprocess.py _list_outputs() throws an error
    w.connect(input_node, 'bold', align_T2star_epi, 'in_file')
    w.connect(input_node, 't2star_fov', align_T2star_epi, 'reference')

    w.connect(input_node, 't2star_whole', align_T2star, 'in_file')
    w.connect(input_node, 't2star_fov', align_T2star, 'reference')

    w.connect(input_node, 't2star_whole', copy, 'in_file')
    w.connect(copy, 'out_file', align_T1_T2star, 'in_file')
    w.connect(input_node, 't1w', align_T1_T2star, 'anat')

    return w
