#!/usr/bin/env python

from distutils.core import setup

with open('README.rst') as readme:
    long_description = readme.read()

requirements = [
    'celery',
    'redis',
]

setup(
    name='celery-redis-task-monitor',
    version='0.0.1',
    description='Celery Task Monitor for Django',
    long_description=long_description,
    author='Omar Khan',
    author_email='omar@omarkhan.me',
    url='https://github.com/omarkhan/celery-redis-task-monitor',
    py_modules=['task_monitor'],
    install_requires=requirements,
    license='MIT',
    keywords='django celery',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
