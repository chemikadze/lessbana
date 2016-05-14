#!/usr/bin/env python

from setuptools import setup

setup(name='Lessbana',
      version='0.1',
      description='Less for LogStash -- better than Kibana!',
      author='Nikolay Sokolov',
      author_email='nsokolov@google.com',
      url='https://github.com/chemikadze/lessbana',
      packages=['lessbana'],
      entry_points='''
        [console_scripts]
        lessbana=lessbana.__main__:main
      '''
      )