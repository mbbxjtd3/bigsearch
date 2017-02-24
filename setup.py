#! /usr/bin/env python


#setup(
#    ext_modules=cythonize("KMP_cythonised_parallel.pyx"),
#)

import os
import sys
import subprocess

from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy


if sys.version_info[0] > 3:
      sys.exit('KMP_genome_search was written on Python 2.7. The version for Python 3 awaits implementation')

setup(
    name='bigsearch',
    url='https://github.com/DeskGen/big-search',
    author='Tomasz Dzida',
    author_email='Tomasz.Dzida@gmail.com',
    description='Case Study in Python searching datasets larger than RAM.',
    packages=["bigsearch"],#find_packages(),
    install_requires=[
        "pysam", "numpy", "cython",
    ],
    tests_require=[
        'pytest',
    ],
    ext_modules=cythonize("bigsearch/*.pyx"),
	include_dirs=[numpy.get_include()]
)


