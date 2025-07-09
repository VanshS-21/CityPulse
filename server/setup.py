"""A setuptools based setup module for the CityPulse data models."""
import setuptools

# Read the contents of your requirements file and filter out comments and empty lines
with open('requirements.txt') as f:
    requirements = [line for line in f.read().splitlines() if line and not line.startswith('#')]

setuptools.setup(
    name='citypulse-data-models',
    version='0.1.0',
    package_dir={'': 'data_models'},
    packages=setuptools.find_packages(where='data_models'),
    install_requires=requirements,
    description='CityPulse data models package.'
)
