from setuptools import setup, find_packages

setup(
    name='StringSheet',
    version='0.1.0',
    description='Manage Android translations using Google Spreadsheets',
    # long_description=readme,
    author='Łukasz Rutkowski',
    author_email='lukus178@gmail.com',
    url='https://github.com/Tunous/StringsSheet',
    license="MIT",
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'httplib2',
        'apiclient',
        'lxml',
        'google-api-python-client'
    ]
)
