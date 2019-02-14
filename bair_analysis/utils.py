from pathlib import Path
from os import rmtree
from nipype import config, logging

PKG_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = PKG_DIR.parent
PROJECT_DIR = SCRIPTS_DIR.parent
SUBJECTS_DIR = PROJECT_DIR / 'subjects'
ANALYSIS_DIR = PROJECT_DIR / 'analysis'
LOG_DIR = ANALYSIS_DIR / 'log'

try:
    rmtree(LOG_DIR)
except FileNotFoundError:
    pass
LOG_DIR.mkdir(exist_ok=True)

config.update_config({
    'logging': {
        'log_directory': LOG_DIR,
        'log_to_file': True,
        },
    'execution': {
        'crashdump_dir': LOG_DIR,
        'keep_inputs': 'true',
        'remove_unnecessary_outputs': 'false',
        },
    })
logging.update_logging(config)
