import os

from setuptools import setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'stringsheet', '__init__.py')) as f:
    exec(f.read(), about)

with open('README.rst') as f:
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
