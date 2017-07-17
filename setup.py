import os
import ast
import shutil
import tempfile
import itertools
from collections import defaultdict
from setuptools import setup, find_packages as _find_packages


VERSION_FILE = './VERSION'
URL_FILE = './URL'

ODOO = 'odoo'
ODOO_ADDONS = 'addons'
ODOO_LOCATION = './%s' % ODOO
ODOO_URL = os.environ.get('ODOO_URL', False)
ODOO_VERSION = os.environ.get('ODOO_VERSION', False)


def _import_manifest(addon):
    manifest_file = os.path.join(ODOO_LOCATION, ODOO_ADDONS, addon, '__manifest__.py')
    with open(manifest_file) as f:
        return ast.literal_eval(f.read())


def _find_addons():
    addons = []
    for package in _find_packages(include=('odoo.addons.*',)):
        parts = package.split('odoo.addons.')[1].split('.')
        if len(parts) != 1:
            continue
        addons.append(parts[0])

    return addons


def find_packages(app=None):

    # Map addons to manifests
    manifests = {
        addon: _import_manifest(addon)
        for addon in _find_addons()
    }

    apps = {
        addon: {}
        for addon, manifest
        in manifests.iteritems()
        if manifest.get('application')
    }
    
    # Create incomming dep graph
    g = defaultdict(set)
    for addon in manifests:
        for dep in manifests[addon].get('depends', []):
            g[dep].add(addon)


    def get_out_dependencies(addon):
        dependencies = set()
        manifest = manifests[addon]
        for dep in manifest.get('depends', []):
            dependencies.add(dep)
            dependencies |= get_out_dependencies(dep)
        
        return dependencies

    def get_in_dependencies(addon):
        dependencies = set(g[addon])
        for dep in g[addon]:
            dependencies |= get_in_dependencies(dep)
        return dependencies

    

    # Find dependant addons for each app that have no direct dependency to another app
    app_addons = {
        app: set([
            dep 
            for dep
            in get_in_dependencies(app)
            if not filter(lambda x: x in apps, manifests[dep].get('depends', []))
        ])
        for app in apps
    }

    # Find addons shared across apps
    shared_addons = reduce(
        lambda acc, (a,b): acc | (app_addons[a] & app_addons[b]),
        itertools.combinations(apps.keys(), 2),
        set()
    )

    print shared_addons

    return []


def bootstrap_odoo(url, location):
    try:
        from pip.index import Link
        from pip.download import unpack_url
    except ImportError:
        return False

    temp = tempfile.mkdtemp()
    unpack_url(Link(url), temp)

    # Move <tempdir>/odoo to ./odoo
    shutil.move(os.path.join(temp, ODOO), location)

    # Move addons from <tempdir>/addons to ./odoo/addons
    # This will put them aside the the base addons.
    for addon in os.listdir(os.path.join(temp, ODOO_ADDONS)):
        src = os.path.join(temp, ODOO_ADDONS, addon)
        dest = os.path.join(location, ODOO_ADDONS, addon)
        shutil.move(src, dest)

    return True


if not os.path.exists(ODOO_LOCATION):
    if os.path.exists(URL_FILE):
        with open(URL_FILE) as f:
            ODOO_URL = f.read().strip()

    if not ODOO_URL or not bootstrap_odoo(ODOO_URL, ODOO_LOCATION):
        raise Exception(
            "Could not bootstrap Odoo. Set ODOO_URL and ensure "
            "Pip is present."
        )


if not ODOO_VERSION:
    if not os.path.exists(VERSION_FILE):
        raise Exception(
            "Could not determine Odoo version. Set ODOO_VERSION."
        )

    with open(VERSION_FILE) as f:
        ODOO_VERSION = f.read().strip()
else:
    with open(VERSION_FILE, 'w') as f:
        f.write(ODOO_VERSION)


if ODOO_URL:
    with open(URL_FILE, 'w') as f:
        f.write(ODOO_URL)



setup(
    name='odooku-odoo',
    version=ODOO_VERSION,
    url='https://github.com/odooku/odooku-odoo',
    author='Raymond Reggers - Adaptiv Design',
    author_email='raymond@adaptiv.nl',
    description=('Odooku Odoo'),
    license='LGPLv3',
    packages=find_packages(),
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
        'odfpy==1.3.5',
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
        'pyusb==1.0.0b1',
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
