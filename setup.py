from setuptools import setup
description = "A Lattice QCD library including statistical, fitting, " \
              "plotting functions and a runner module to help organise " \
              "projects."
setup(
    name='pyon',
    version='0.0.5',
    packages=['pyon', 'pyon.lib', 'pyon.test', 'pyon.runner',
              'pyon.lib.io'
              ],
    url='',
    license='',
    author='Shane Drury',
    author_email='shane.r.drury@gmail.com',
    description=description,
    install_requires=['numpy', 'scipy', 'simplejson', 'Jinja2', 'django',
                      ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    entry_points={
        'console_scripts': ['pyon-admin = '
                            'pyon.core.management:execute_from_command_line'],
    }
)
