from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='bcpy',
    version='0.1dev',
    description='Tool for analysis of EEG BCI (brain-computer interface) data',
    author='Filip Skola',
    author_email='xskola@mail.muni.cz',
    packages=['bcpy',],
    license='MIT',
    keywords='bci eeg brain-computer',
    long_description=long_description,
)
