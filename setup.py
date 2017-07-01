import os, sys
import shutil
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from pip.index import Link
from pip.download import unpack_url

ODOO = 'odoo'
ODOO_LOCATION = './%s' % ODOO
ODOO_URL = 'https://github.com/odoo/odoo/archive/10.0.tar.gz'


def bootstrap_odoo(url, location):
    unpack_url(Link(url), location)


if not os.path.exists(ODOO_LOCATION):
    bootstrap_odoo(ODOO_URL, ODOO_LOCATION)
    for addon in os.listdir(os.path.join(ODOO_LOCATION, 'addons')):
        src = os.path.join(ODOO_LOCATION, 'addons', addon)
        dest = os.path.join(ODOO_LOCATION, 'odoo', 'addons', addon)
        shutil.move(src, dest)


setup(
    name='odooku-odoo',
    version='10.0.1',
    url='https://github.com/odooku/odooku-odoo',
    author='Raymond Reggers - Adaptiv Design',
    author_email='raymond@adaptiv.nl',
    description=('Odooku Odoo'),
    license=license,
    packages=find_packages(ODOO),
    package_dir={'': ODOO_LOCATION},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Babel==2.3.4',
        'decorator==4.0.10',
        'docutils==0.12',
        'ebaysdk==2.1.4',
        'feedparser==5.2.1',
        'gevent==1.1.2',
        'greenlet==0.4.10',
        'jcconv==0.2.3',
        'Jinja2==2.8',
        'lxml==3.5.0',
        'Mako==1.0.4',
        'MarkupSafe==0.23',
        'mock==2.0.0',
        'ofxparse==0.15',
        'passlib==1.6.5',
        'Pillow==3.4.1',
        'psutil==4.3.1',
        'psycogreen==1.0',
        'psycopg2==2.6.2',
        'pydot==1.2.3',
        'pyparsing==2.1.10',
        'pyPdf==1.13',
        'pyserial==3.1.1',
        'Python-Chart==1.39',
        'python-dateutil==2.5.3',
        'python-ldap==2.4.27',
        'python-openid==2.2.5',
        'pytz==2016.7',
        'pyusb==1.0.0',
        'PyYAML==3.12',
        'qrcode==5.3',
        'reportlab==3.3.0',
        'requests==2.11.1',
        'six==1.10.0',
        'suds-jurko==0.6',
        'vatnumber==1.2',
        'vobject==0.9.3',
        'Werkzeug==0.11.11',
        'wsgiref==0.1.2',
        'XlsxWriter==0.9.3',
        'xlwt==1.1.2',
        'xlrd==1.0.0'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
    ],
)
