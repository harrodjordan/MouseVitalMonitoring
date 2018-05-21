import Cython
from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'Test',
  ext_modules = cythonize("test.pyx"),
)