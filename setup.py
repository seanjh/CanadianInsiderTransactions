try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Canadian Insider Transactions',
    version='0.1',
    packages=['sedi_transactions'],
    url='',
    license='The MIT License (MIT)',
    author='Sean J. Herman',
    author_email='seanherman@gmail.com',
    description='',
    install_requires= [
        'requests >= 2.2',
        'lxml >= 3.3',
        'docopt'
    ]
)
