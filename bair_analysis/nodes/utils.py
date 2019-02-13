from nipype.interfaces.utility import IdentityInterface
from nipype.pipeline.engine import Node


input_node = Node(IdentityInterface(fields=[
        'func',
        'anat',
        'events',
        ]), name='input')