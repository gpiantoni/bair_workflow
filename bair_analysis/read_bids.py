from xelo2bids.bids_tree import create_bids
from pandas import read_pickle
from xelo2bids.core.constants import TASKS_PATH

from .utils import PROJECT_DIR


def create_bids_beilen():

    DF_TASKS = read_pickle(str(TASKS_PATH))

    beilen_tasks = DF_TASKS.loc[
        (DF_TASKS.SubjectCode == 'beilen')
        & (DF_TASKS.Technique.isin(('MRI', 'fMRI')))
    ].index.tolist()

    create_bids(
        PROJECT_DIR / 'subjects',
        beilen_tasks,
        deface=False)
