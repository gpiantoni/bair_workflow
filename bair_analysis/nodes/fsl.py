from nipype.interfaces.fsl import BET
from nipype.pipeline.engine import Node


# node skull
skull = Node(interface=BET(), name="skull_stripping")