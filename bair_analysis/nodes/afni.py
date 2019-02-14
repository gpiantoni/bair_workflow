from nipype import Node
from nipype.interfaces.afni import AlignEpiAnatPy, Copy

copy_afni = Node(Copy(), name='convert_to_afni')

align_T1_T2star = Node(AlignEpiAnatPy(), name='align_T1_T2star')
align_T1_T2star.inputs.tshift = 'off'
align_T1_T2star.inputs.volreg = 'off'
align_T1_T2star.inputs.args = '-cost lpc -partial_coverage -anat_has_skull yes -Allineate_opts -interp NN -twopass -warp affine_general  -final wsinc5'
align_T1_T2star.inputs.epi_base = 1
align_T1_T2star.inputs.epi2anat = True
align_T1_T2star.inputs.epi_strip = 'None'
align_T1_T2star.inputs.outputtype = 'NIFTI_GZ'
