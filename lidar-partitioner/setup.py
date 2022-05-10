from setuptools import setup, find_packages

setup(
    name='lidarpartitioner',
    version='1.0.0',
    packages=find_packages(include=['lidarpartitioner']),
    install_requires=[
        'numpy',
        'laspy>=2.0'
    ]
)