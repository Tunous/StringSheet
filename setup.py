from setuptools import setup


def readme():
    with open('README.rst') as file:
        return file.read()


setup(
    name='StringSheet',
    version='0.1.0',
    description='Manage Android translations using Google Spreadsheets',
    long_description=readme(),
    author='Łukasz Rutkowski',
    author_email='lukus178@gmail.com',
    url='https://github.com/Tunous/StringsSheet',
    license="MIT",
    packages=['stringsheet'],
    install_requires=[
        'httplib2',
        'apiclient',
        'lxml',
        'google-api-python-client'
    ],
    scripts=['bin/stringsheet-cli.py']
)
