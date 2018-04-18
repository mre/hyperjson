from setuptools import setup
from setuptools_rust import Binding, RustExtension

#
setup(name='hyperjson',
      version='0.1',
      rust_extensions=[
          RustExtension('hyperjson._hyperjson',
                        'Cargo.toml', binding=Binding.PyO3)],
      packages=['hyperjson'],
      # rust extensions are not zip safe, just like C-extensions.
      zip_safe=False)
