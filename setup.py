import sys
from setuptools import setup

setup(name='hyperjson',
      version='0.1',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Rust',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
      ],
      packages=['hyperjson'],
      package_dir={'': 'package'},
      zip_safe=False)
