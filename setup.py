from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pyfedwatch',
    version='1.1.0',
    description='Python Implementation of the CME FedWatch Tool for Estimating Probabilities of Federal Funds Rate Changes at Upcoming FOMC Meetings.',
    author='ALI RAHIMI',
    author_email='a.rahimi.aut@gmail.com',
    url='https://github.com/ARahimiQuant/pyfedwatch',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'pandas>=2.1.0',
        'numpy>=1.25.2',
        'python-dateutil>=2.8.2',
        'pytz>=2023.3.post1',
        'tzdata>=2023.3',
        'matplotlib>=3.8.0',
        'holidays>=0.32',
        'openpyxl>=3.1.2',
        'pandas_datareader==0.10.0',
    ],
    license='Apache-2.0',
)