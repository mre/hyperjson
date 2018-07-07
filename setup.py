import sys
from setuptools import setup

try:
    from setuptools_rust import Binding, RustExtension
except ImportError:
    import subprocess
    errno = subprocess.call(
        [sys.executable, '-m', 'pip', 'install', 'setuptools-rust'])
    if errno:
        print("Please install setuptools-rust package")
        raise SystemExit(errno)
    else:
        from setuptools_rust import Binding, RustExtension

setup_requires = ['setuptools-rust>=0.9.2']
install_requires = []

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
      rust_extensions=[
          RustExtension('hyperjson._hyperjson', 'Cargo.toml', binding=Binding.PyO3)],
      packages=['hyperjson'],
      package_dir={'':'package'},
      zip_safe=False)
