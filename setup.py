import os

from io import open
from setuptools import setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'stringsheet', '__init__.py'), encoding='utf-8') as f:
    for line in f:
        if line.startswith('__'):
            (key, value) = line.split('=')
            about[key.strip()] = value.strip().strip('\'')

with open('README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    packages=['stringsheet'],
    install_requires=[
        'httplib2',
        'apiclient',
        'lxml',
        'google-api-python-client'
    ],
    entry_points={
        'console_scripts': [
            'stringsheet = stringsheet.cli:main'
        ]
    }
)
