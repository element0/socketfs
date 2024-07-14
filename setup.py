from setuptools import setup, find_packages

setup(
    name='socketfs',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'fs>=2.0',  # Minimum version 2.0 of pyfilesystem
    ],
    # Other metadata
    author='Raygan Henley',
    author_email='raygan@raygan.com',
    description='Pyfilesystem proxy over socket.',
    url='https://github.com/element0/socketfs',
)
