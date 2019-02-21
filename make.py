#!/usr/bin/env python3

from argparse import ArgumentParser
from shutil import rmtree
from subprocess import run

from bair_analysis.utils import (
    SUBJECTS_DIR,
    ANALYSIS_DIR,
    )
from bair_analysis.read_bids import (
    create_bids_beilen,
    )


parser = ArgumentParser(prog='make',
                        description=f'Run ')
parser.add_argument('-g', '--get_files', action='store_true',
                    help='download datasets to run tests')
parser.add_argument('-t', '--tests', action='store_true',
                    help='run tests')
parser.add_argument('-c', '--clean', action='store_true',
                    help='clean up docs (including intermediate files)')
parser.add_argument('--all', action='store_true',
                    help='clean up, read data and run analysis')

args = parser.parse_args()


def _tests():

    CMD = ['pytest',
           '--disable-warnings',
           '--capture=no',
           '-v',
           '--cov=bair_analysis',
           '--cov-report=html',
           'tests/test_spatialobjects.py',
           ]

    output = run(CMD)

    return output.returncode


def _get_files():
    create_bids_beilen()


def _clean_all():
    rmtree(SUBJECTS_DIR, ignore_errors=True)
    rmtree(ANALYSIS_DIR, ignore_errors=True)


if __name__ == '__main__':
    returncode = 0

    if args.all or args.clean:
        _clean_all()

    if args.all or args.get_files:
        _get_files()

    if args.all or args.tests:
        returncode = _tests()

    exit(returncode)
