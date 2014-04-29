from setuptools import setup

setup(
    name='pyon',
    version='0.0.3',
    packages=['pyon', 'pyon.lib', 'pyon.test', 'pyon.runner',
              'pyon.lib.io'
              ],
    url='',
    license='',
    author='Shane Drury',
    author_email='shane.r.drury@gmail.com',
    description='',
    install_requires=['numpy', 'scipy', 'simplejson', 'Jinja2'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
