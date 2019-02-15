from nipype.pipeline.engine import Node, Workflow
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.spm import Realign


def create_workflow_preproc_spm():
    input_node = Node(IdentityInterface(fields=[
        'bold',
        ]), name='input')

    # node realign
    realign = Node(interface=Realign(), name="realign")
    realign.inputs.register_to_mean = True

    w = Workflow(name='preproc_spm')
    w.connect(input_node, 'bold', realign, 'in_files')
