from setuptools import setup
readme = open('README.md').read()
setup(name='notehub',
      version='0.3',
      author='Sean Watson',
      license='MIT',
      description='A simple wrapper for the Notehub.org API.',
      long_description=readme,
      keywords='notehub',
      url='https://github.com/seanwatson/notehub',
      py_modules=['notehub'],
      install_requires=['requests'])
