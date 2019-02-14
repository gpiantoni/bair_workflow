from nipype import Node, Workflow
from nipype.interfaces.afni import AlignEpiAnatPy, Copy
from nipype.interfaces.fsl import FLIRT
from nipype.interfaces.utility import IdentityInterface


def create_workflow_realign():

    input = Node(IdentityInterface(fields=[
        '7T_epi',
        '7T_T2star_fov',
        '7T_T2star_whole',
        '7T_T1w',
        ]), name='input')
    # output = Node(IdentityInterface(fields=['7T_T1w_reg_affine', '7T_T1w_reg_SyN']), name='output')

    copy = Node(Copy(), name='convert_to_afni')

    align_T2star = Node(FLIRT(), name='align_T2star')
    align_T2star.inputs.cost = 'mutualinfo'
    align_T2star.inputs.dof = 6
    align_T2star.inputs.output_type = 'NIFTI_GZ'

    align_T2star_epi = Node(FLIRT(), name='align_T2star_epi')
    align_T2star_epi.inputs.cost = 'mutualinfo'
    align_T2star_epi.inputs.dof = 12
    align_T2star_epi.inputs.no_search = True
    align_T2star_epi.inputs.output_type = 'NIFTI_GZ'

    align_T1_T2star = Node(AlignEpiAnatPy(), name='align_T1_T2star')
    align_T1_T2star.inputs.tshift = 'off'
    align_T1_T2star.inputs.volreg = 'off'
    align_T1_T2star.inputs.args = '-cost lpc -partial_coverage -anat_has_skull yes -Allineate_opts -interp NN -twopass -warp affine_general  -final wsinc5'
    align_T1_T2star.inputs.epi_base = 1
    align_T1_T2star.inputs.epi2anat = True
    align_T1_T2star.inputs.epi_strip = 'None'
    align_T1_T2star.inputs.outputtype = 'NIFTI_GZ'

    w = Workflow('realign_7T_to_epi')

    # it's necessary to convert to AFNI for nipype, otherwise afni/preprocess.py _list_outputs() throws an error
    w.connect(input, '7T_epi', align_T2star_epi, 'in_file')
    w.connect(input, '7T_T2star_fov', align_T2star_epi, 'reference')

    w.connect(input, '7T_T2star_whole', align_T2star, 'in_file')
    w.connect(input, '7T_T2star_fov', align_T2star, 'reference')

    w.connect(input, '7T_T2star_whole', copy, 'in_file')
    w.connect(copy, 'out_file', align_T1_T2star, 'in_file')
    w.connect(input, '7T_T1w', align_T1_T2star, 'anat')

    return w
