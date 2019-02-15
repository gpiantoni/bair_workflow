from nipype.interfaces.fsl import BET, FLIRT, EpiReg
from nipype.pipeline.engine import Node

# node skull
skull = Node(interface=BET(), name="skull_stripping")


coreg_epi2fov = Node(FLIRT(), name='epi_2_fov')
coreg_epi2fov.inputs.cost = 'mutualinfo'
coreg_epi2fov.inputs.dof = 12
coreg_epi2fov.inputs.no_search = True
coreg_epi2fov.inputs.output_type = 'NIFTI_GZ'

coreg_fov2whole = Node(FLIRT(), name='fov_2_whole')
coreg_fov2whole.inputs.cost = 'mutualinfo'
coreg_fov2whole.inputs.dof = 6
coreg_fov2whole.inputs.output_type = 'NIFTI_GZ'

coreg_whole2t1w = Node(EpiReg(), name='whole_2_t1w')
