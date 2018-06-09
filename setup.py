from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='xawscf',
    version='0.0.1',
    description='Manages aws cloudformation stacks deployment',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dmitry Bogomolov',
    license='MIT',
    packages=find_packages(),
    install_requires=['boto3', 'PyYAML'],
    scripts=['bin/xawscf'],
    test_suite='test'
)
