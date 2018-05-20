from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'Mouse-UI',
  ext_modules = cythonize("mouse-UI-cython.pyx"),
)