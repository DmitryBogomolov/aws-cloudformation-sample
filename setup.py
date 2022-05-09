from setuptools import setup, find_packages

with open('README.md', mode='r', encoding='utf-8') as file_object:
    long_description = file_object.read()

with open('requirements.txt', mode='r', encoding='utf-8') as file_object:
    requirements = file_object.readlines()

setup(
    name='xawscf',
    version='0.0.1',
    description='Manages aws cloudformation stacks deployment',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dmitry Bogomolov',
    license='MIT',
    packages=find_packages(),
    install_requires=requirements,
    scripts=['bin/xawscf'],
    test_suite='run_tests'
)
