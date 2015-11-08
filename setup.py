from setuptools import setup
from pip.req import parse_requirements

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
install_requires = [
    str(ir.req) for ir in parse_requirements('requirements.txt')
]

setup(
    name='sql_query_dict',
    version='0.3',
    description='express sql queries as python dictionaries',
    url='http://github.com/PlotWatt/sql_query_dict',
    author='PlotWatt',
    author_email='zdwiel@plotwatt.com',
    license='Apache',
    py_modules=['sql_query_dict'],
    install_requires=install_requires,
)
