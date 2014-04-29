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
)
