from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'C Board',
  ext_modules = cythonize("CBoard.pyx"),
)