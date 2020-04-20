import os
from setuptools import setup

# read in README
this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, 'README.md'), 'rb') as f:
    long_description = f.read().decode().strip()

# requirements
install_requires = [
    "hop-client >= 0.0.4", "requests", "slackclient"
]
extras_require = {
    'dev': ['pytest', 'pytest-console-scripts', 'pytest-cov', 'flake8', 'flake8-black', 'pytest-datadir'],
    'docs': ['sphinx', 'sphinx_rtd_theme', 'sphinxcontrib-programoutput'],
}

setup(
    name = 'hop-slack-app',
    description = 'This is an application for Hop on Slack where you can receive GCN messages',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/scimma/scimma-slack-app',
    author = 'Shereen Elsayed',
    author_email = 's_elsayed@ucsb.edu',
    license = 'BSD 3-Clause',
    packages = ['hop', 'hop.apps', 'hop.apps.slack'],
        entry_points = {
        'console_scripts': [
            'hop-slack = hop.apps.slack.__main__:main',
        ],
    },

    python_requires = '>=3.6.*',
    install_requires = install_requires,
    extras_require = extras_require,
    setup_requires = ['setuptools_scm'],
    use_scm_version = {
        'write_to': 'hop/apps/slack/_version.py'
    },

    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'License :: OSI Approved :: BSD License',
    ],

)
