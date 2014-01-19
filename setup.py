from setuptools import setup
readme = open('README.md').read()
setup(name='notehub',
      version='0.1',
      author='Sean Watson',
      license='MIT',
      description='A simple wrapper for the Notehub.org API.',
      long_description=readme,
      py_modules=['notehub'])
