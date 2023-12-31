from setuptools import setup, find_packages
from mst_gateway import version


with open('README.md') as f:
    README = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()

setup(
    name='mst-gateway',
    python_requires='>=3.9.0',
    version=version.VERSION,
    packages=find_packages(exclude=('tests', 'tests.*')),
    author='Vladimir Belinskiy',
    author_email='belka158@gmail.com',
    description='MSTrade stocks gateway',
    license=LICENSE,
    long_description=README,
    url='ssh://belka158@bitbucket.org/mstrade_dev/mst-gateway.git',
    install_requires=[
        'websockets==10.3',
        'httpx[socks]==0.23.0'
    ],
    extras_require={
        'mysql': ['mysql-connector-python'],
        'pgsql': ['psycopg2']
    },
    entry_points={
        'console_scripts': [
            'mstgw = mst_gateway.app:main'
        ]
    },
)
