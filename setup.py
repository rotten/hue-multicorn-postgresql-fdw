## This is a very simple setup for the module that allows us to create foreign data wrappers in PostgreSQL for the Philips Hue System.
## It is based on the Multicorn README and the Hive FDW example.
##
from distutils.core import setup

setup(
  name='hue_fdw',
  version='0.1',
  author='Rick Otten',
  author_email='rotten@windfish.net',
  license='Postgresql',
  packages=['hue_fdw'],
  url='https://github.com/rotten/hue-multicorn-postgresql-fdw'
)

