from setuptools import setup, find_packages

# Boilerplate for integrating with PyTest
from setuptools.command.test import test
import sys
import os

# Sanic only supports uvloop on POSIX platforms
if not os.name == 'posix':
    os.environ['SANIC_NO_UVLOOP'] = 'true'


class PyTest(test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]
    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

# The actual setup metadata
setup(
    name='binah',
    version='0.0.1',
    description='A framework for all things related to embeddings across heterogeneous data.',
    long_description=open("README.rst").read(),
    keywords='machine_learning artificial_intelligence devops',
    author='JJ Ben-Joseph',
    author_email='opensource@phrostbyte.com',
    python_requires='>=3.6',
    url='https://etzai.github.io/',
    license='Apache',
    classifiers=[
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent'
    ],
    packages=find_packages(),
    install_requires=['tqdm', 'sqlalchemy', 'python-dateutil', 'annoy', 
                      'tensorflow_hub', 'numpy', 'scikit-image',
                      'sanic', 'opencv-python', 'pytube', 'piexif'],
    extras_require={
        'gpu': ['tensorflow-gpu >= 1.8'],
        'cpu': ['tensorflow >= 1.8']
    },
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'etz = binah.__main__:main',
        ],
    },
    cmdclass = {'test': PyTest}
)