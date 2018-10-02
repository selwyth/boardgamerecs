from setuptools import setup, find_packages

setup(
    name="boardgamerecs",
    description='',
    version="0.1",
    packages=find_packages(),
    scripts=['scripts/generate_genomes'],
    install_requires=['django'],
    author="selwyth",
    author_email="selwyth@gmail.com",
    license="PSF",
    keywords="board game recommendations",
)