from nipype.interfaces.fsl import BET, FLIRT
from nipype.pipeline.engine import Node

# node skull
skull = Node(interface=BET(), name="skull_stripping")


align_T2star = Node(FLIRT(), name='align_T2star')
align_T2star.inputs.cost = 'mutualinfo'
align_T2star.inputs.dof = 6
align_T2star.inputs.output_type = 'NIFTI_GZ'

align_T2star_epi = Node(FLIRT(), name='align_T2star_epi')
align_T2star_epi.inputs.cost = 'mutualinfo'
align_T2star_epi.inputs.dof = 12
align_T2star_epi.inputs.no_search = True
align_T2star_epi.inputs.output_type = 'NIFTI_GZ'
