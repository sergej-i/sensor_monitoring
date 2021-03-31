''' package '''

import os
# import sys
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# CONFIG_PATH = os.path.join(sys.prefix, 'bin/sensor_monitoring_config')
CONFIG_PATH = os.path.join('bin/sensor_monitoring_config')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='sensor_monitoring',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='Private',
    description='keywords: process, thread, monitoring',
    long_description=README,
    url='https://www.example.com/',
    author='Sergey I',
    author_email='yourname@example.com',
    install_requires=[
        'jsonschema==3.2.0',
        'wheel'
    ],
    data_files=[
        (
            CONFIG_PATH,
            [
                'sensor_monitoring_config/monitoring.json',
                'sensor_monitoring_config/monitoring.schema.json'
            ]
        )
    ],
    scripts=['sensor_monitor.py', 'sensor1.py', 'sensor2.py'],
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
    ],
)
