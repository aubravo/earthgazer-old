#!/usr/bin/env python

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(name='gxiba',
      version='1.0.0.dev',
      description='Toolbox for data preparation and neural network training for the gxiba project',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/aubravo/gxiba",
      author='Alvaro Bravo',
      author_email='alvaroubravo@gmail.com',
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Education",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: Unix",
                   "Programming Language :: Python :: 3.8",
                   "Programming Language :: SQL",
                   "Programming Language :: Unix Shell",
                   "Topic :: Scientific/Engineering :: Artificial Intelligence",
                   "Topic :: Scientific/Engineering :: Astronomy"],
      keywords="neural networks, image processing, satellite imaging",
      package_dir={"": "gxiba"},
      packages=find_packages(where="gxiba"),
      python_requires=">=3.8, <4"
      )
