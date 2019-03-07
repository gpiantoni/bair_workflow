from bair_analysis.utils import ANALYSIS_DIR, SUBJECTS_DIR
from bair_analysis.workflows.temporalpatterns import (
    create_workflow_temporalpatterns_7T,
    )


def test_workflow_temporalpatterns_7T():
    w = create_workflow_temporalpatterns_7T()

    input_node = w.get_node('input')
    input_node.inputs.subject = 'beilen'
    w.base_dir = str(ANALYSIS_DIR)
    w.write_graph(graph2use='flat')
    w.write_graph(graph2use='colored')

    w.run(plugin='MultiProc')
