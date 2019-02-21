from setuptools import setup, find_packages

setup(
    name='bair_analysis',
    description='Tools to analyze data structured as BIDS in Python',
    author="Gio Piantoni",
    license='MIT',
    packages=find_packages(exclude=('test', )),
    install_requires=[
        'bidso',
        'wonambi',
        'nipype',
        ],
    extras_require={
        'test': [  # to run tests
            'pytest',
            'pytest-cov',
            'neuropythy',
            ],
        },
    )
