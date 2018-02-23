import os
import fnmatch
import ast
import shutil
import tempfile
import itertools
import functools
import json
from collections import defaultdict, OrderedDict
from setuptools import Command, setup, find_packages
from setuptools.command.sdist import sdist as sdist_orig


DEFAULT_ODOO_URL = 'https://github.com/odoo/odoo/archive/0da5d63f526398022f918bcfdf082c75f26a8b2e/11.0.tar.gz'
DEFAULT_ODOO_VERSION = '11.0.4'


EXTENSIONS = [
    'css',
    'csv',
    'doc',
    'eml',
    'eot',
    'gif',
    'html',
    'ico',
    'jpeg',
    'jpg',
    'js',
    'less',
    'md',
    'mp3',
    'ods',
    'ogg',
    'otf',
    'pdf',
    'png',
    'rml',
    'rng',
    'rst',
    'sass',
    'sql',
    'svg',
    'template',
    'txt',
    'ttf',
    'woff',
    'woff2',
    'wsdl',
    'xls',
    'xlsx',
    'xsd',
    'xsl',
    'xml',
    'yml'
]


ODOO_REQUIREMENTS = [
    'Babel==2.3.4',
    'decorator==4.0.10',
    'docutils==0.12',
    'gevent==1.2.2',
    'greenlet==0.4.10',
    'html2text==2017.10.4',
    'Jinja2==2.8',
    'lxml==3.5.0',
    'Mako==1.0.7',
    'mock==2.0.0',
    'num2words==0.5.5',
    'passlib==1.6.5',
    'Pillow==4.3.0',
    'psutil==5.2.2',
    'psycopg2==2.7.3.2',
    'PyPDF2==1.26',
    'python-dateutil==2.5.3',
    'pytz==2016.7',
    'PyYAML==3.12',
    'reportlab==3.4.0',
    'requests==2.11.1',
    'six==1.10.0',
    'vatnumber==1.2',
    'Werkzeug==0.11.11',
    'XlsxWriter==0.9.3',
    'xlwt==1.3.0'
]


REQUIREMENTS = {
    'suds-jurko==0.6': ['base_vat_autocomplete'],
    'pyldap==2.4.28': ['auth_ldap'],
    'pyserial==3.1.1': ['hw_blackbox_be', 'hw_scale', 'hw_escpos'],
    'pyusb==1.0.0': ['hw_escpos'],
    'qrcode==5.3': ['hw_escpos'],
    'vobject==0.9.3': ['calendar'],
    'feedparser==5.2.1': ['mail'],
    'xlrd==1.0.0': ['base_import'],
    'phonenumbers==8.8.11': ['phone_validation']
}


ODOO = 'odoo'
ODOO_ADDONS = 'addons'
ODOO_LOCATION = './%s' % ODOO

FEATURE = os.environ.get('FEATURE', None)
LANGUAGES = [lang.strip() for lang in os.environ.get('LANGUAGES', '').split(',') if lang.strip()]
ODOO_URL = os.environ.get('ODOO_URL', DEFAULT_ODOO_URL)
ODOO_VERSION = os.environ.get('ODOO_VERSION', DEFAULT_ODOO_VERSION)


def topological_sort(graph):
    """
    Performs a dependency based topological sort. Keeping a stable order.
    Arguments:
        - graph: An (ordered) dictionary representing a directed graph. Where each item
        is { node: [set or list of incomming edges (depedencies)] }
    """

    # Copy graph for lookup purposes
    incomming = OrderedDict(
        [
            (node, list(edges)) for node, edges in graph.items()
        ]
    )

    # Try to output nodes in initial order
    nodes = [node for node in incomming.keys()]

    # Keep a stack in order to detect cyclic dependencies
    stack = []
    while nodes:
        # Get first node
        n = nodes[0]

        # See if this node has dependencies which haven't yet been
        # outputted.
        remaining = [node for node in reversed(incomming[n]) if node in nodes]
        if remaining:
            if n not in stack:
                stack.append(n)
            else:
                raise Exception(
                    "Cyclic dependency"
                    " detected {0}".format(
                        '->'.join(
                            [
                                str(x) for x in (
                                    stack + [n]
                                )
                            ]
                        )
                    )
                )
            for m in remaining:
                # Place dependency at front
                nodes.remove(m)
                nodes.insert(0, m)
        else:
            # No dependencies left, output
            yield nodes.pop(0)


def _import_manifest(addon):
    manifest_file = os.path.join(ODOO_LOCATION, ODOO_ADDONS, addon, '__manifest__.py')
    with open(manifest_file) as f:
        return ast.literal_eval(f.read())


def _find_addons():
    addons = []
    for package in find_packages(include=('odoo.addons.*',)):
        parts = package.split('odoo.addons.')[1].split('.')
        if len(parts) != 1:
            continue
        addons.append(parts[0])

    return addons


def _find_addon_packages(addon):
    return find_packages(include=('odoo.addons.%s' % addon, 'odoo.addons.%s.*' % addon))


def _find_package_data_files(package, excludes, package_dir=".", languages=None):
    path = os.path.join(*([package_dir] + package.split('.')))
    exclude_paths = [
        os.path.join(*([package_dir] + exclude.split('.')))
        for exclude in excludes
        if exclude != package
    ]

    files = set()
    for root, dirnames, filenames in os.walk(path):
        if root in exclude_paths:
            dirnames[:] = []
            continue
        
        for ext in EXTENSIONS:
            files |= set([
                os.path.relpath(os.path.join(root, match), path)
                for match in fnmatch.filter(filenames, '*.%s' % ext)
            ])

        if languages:
            for language in languages:
                files |= set([
                    os.path.relpath(os.path.join(root, match), path)
                    for match in fnmatch.filter(filenames, '%s.po' % language)
                ])
        else:
            # Find all translation files
            files |= set([
                os.path.relpath(os.path.join(root, match), path)
                for match in fnmatch.filter(filenames, '*.po')
            ])
            
    
    return list(files)


def analyze():
    # Map addons to manifests
    manifests = {
        addon: _import_manifest(addon)
        for addon in _find_addons()
    }

    # Get apps
    apps = {
        addon: {
            'app_dependencies': set()
        }
        for addon, manifest
        in manifests.items()
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

    
    # Find dependant and dependency addons for each app
    app_addons = {}
    for app in apps:
        addons = set([app])
        addons |= get_in_dependencies(app)
        for addon in list(addons):
            addons |= get_out_dependencies(addon)
        
        app_addons[app] = addons

    # Find addons shared across apps
    shared_addons = functools.reduce(
        lambda acc, ab: acc | (app_addons[ab[0]] & app_addons[ab[1]]),
        itertools.combinations(apps.keys(), 2),
        set()
    )

    # Get unique addons for each app
    app_addons = {
        app: (app_addons[app] - shared_addons)
        for app in apps
    }

    # Get inter-app dependencies and filter out truly independent addons
    base_addons = set()
    for addon in list(shared_addons):
        deps = get_out_dependencies(addon) | set([addon])
        app_dependencies = set([
            app
            for app in apps
            if len(get_in_dependencies(app) & deps) > 0
        ])

        if addon in apps:
            # Dealing with an app
            app_addons[addon].add(addon)
            apps[addon].update({
                'app_dependencies': set(app_dependencies)
            })
        elif not app_dependencies:
            # App independent addon
            base_addons.add(addon)
        else:
            continue

        # No longer a shared addon
        shared_addons.remove(addon)

    # Filter out addons according to  already existing inter app dependencies
    for addon in list(shared_addons):
        out_deps = get_out_dependencies(addon) | set([addon])
        in_deps = get_in_dependencies(addon)
        app_dependencies = set([
            app
            for app in apps
            if len(get_in_dependencies(app) & out_deps) > 0
        ])
        
        dependant_apps = set([
            app
            for app in apps
            if app in in_deps
        ])

        # Find single app dependency that fulfilles all other app dependencies for
        # this addon.
        for app in app_dependencies:
            fulfilles_in = len((app_dependencies - set([app])) - apps[app]['app_dependencies']) == 0
            fulfilles_out = not dependant_apps or all([
                app in apps[dep]['app_dependencies']
                for dep in 
                dependant_apps
            ])

            if fulfilles_in and fulfilles_out:
                break
        else:
            continue

        app_addons[app].add(addon)

        # No longer a shared addon
        shared_addons.remove(addon)
    
    # Filter out apps that are dependant on shared addons
    for app in list(apps):
        shared_deps =  (get_out_dependencies(app) | get_in_dependencies(app)) & shared_addons
        app_addons[app] |= shared_deps
    
    # Combine everything
    # Find unreferenced addons
    remaining_addons = set(manifests.keys()) - base_addons
    for app in apps:
        remaining_addons -= app_addons[app]
        shared_addons -= app_addons[app]
        apps[app]['addons'] = set(app_addons[app])
    
    for addon in list(remaining_addons):
        manifest = manifests[addon]
        if manifest.get('auto_install'):
            remaining_addons.remove(addon)
            base_addons.add(addon)
    
    assert not shared_addons
    return apps, base_addons, remaining_addons


def configure(version, feature=None, languages=None):

    apps, base_addons, extra_addons = analyze()

    name = 'odooku-odoo%s' % ('' if not feature else '-%s' % feature)
    description = ''
    install_requires = set()
    package_dir = None
    packages = set()
    addons = set()

    if not feature:
        description = 'Odoo full installation'
        packages |= set(find_packages(exclude=('odoo.addons.*',)))
        addons |= set(base_addons) | set(extra_addons) | set(itertools.chain(*[
            apps[app]['addons']
            for app in apps
        ]))
        install_requires |= set(ODOO_REQUIREMENTS)
    elif feature == 'base':
        description = 'Odoo base installation'
        packages |= set(find_packages(exclude=('odoo.addons.*',)))
        addons |= set(base_addons)
        install_requires |= set(ODOO_REQUIREMENTS)
    else:
        packages.add('odoo.addons')
        install_requires.add('odooku-odoo-base==%s' % version)
        if feature in apps:
            manifest = _import_manifest(feature)
            description = 'Odoo addons for the %s app' % manifest.get('name')
            addons |= set(apps[feature]['addons'])
            for dep in apps[feature]['app_dependencies']:
                install_requires.add('odooku-odoo-%s==%s' % (dep, version))
        elif feature == 'addons':
            description = 'All addons for Odoo'
            install_requires.add('odooku-odoo-extra==%s' % version)
            for app in apps:
                install_requires.add('odooku-odoo-%s==%s' % (app, version))
        elif feature == 'extra':
            description = 'Extra Odoo addons'
            addons |= set(extra_addons)
        else:
            raise Exception("Unknown feature '%s'" % feature)

    # Map requirements to addons
    addon_requirements = defaultdict(set)
    for req in REQUIREMENTS:
        for addon in REQUIREMENTS[req]:
            addon_requirements[addon].add(req)

    for addon in addons:
        packages |= set(_find_addon_packages(addon))
        if addon in addon_requirements:
            install_requires |= addon_requirements[addon]

    package_data = {
        package: _find_package_data_files(package, packages, languages=languages)
        for package in packages
        if package not in ('odoo.addons',)
    }

    try:
        import pypandoc
        long_description = pypandoc.convert('README.md', 'rst')
    except(IOError, ImportError):
        long_description = open('README.md').read()
    
    return {
        'name': name,
        'version': version,
        'description': description,
        'long_description': long_description,
        'package_dir': package_dir,
        'packages': list(packages),
        'package_data': package_data,
        'install_requires': list(install_requires)
    }


def bootstrap_odoo(url, location):
    try:
        from pip.index import Link
        from pip.download import unpack_url
    except ImportError:
        return False
    
    print('Boostrapping Odoo from %s' % url)
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


def deunicodify_hook(pairs):
    new_pairs = []
    for key, value in pairs:
        if isinstance(value, str):
            value = value.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        new_pairs.append((key, value))
    return dict(new_pairs)


if not os.path.exists(ODOO_LOCATION):
    if not ODOO_URL:
        raise Exception("Could not bootstrap Odoo. Set ODOO_URL.")
    if not bootstrap_odoo(ODOO_URL, ODOO_LOCATION):
        raise Exception("Could not bootstrap Odoo. Ensure pip is installed.")


# In case of source distributions there is no complete odoo directory
# so configuration is impossible the setup.json file contains all
# setup variables that where previously configured.
if not os.path.exists('./setup.json'):
    if not ODOO_VERSION:
        raise Exception("Could not configure. Set ODOO_VERSION.")
    conf = configure(ODOO_VERSION, feature=FEATURE, languages=LANGUAGES)
else:
    with open('./setup.json', 'r') as f:
        conf = json.load(f, object_pairs_hook=deunicodify_hook)


class sdist(sdist_orig):
    def make_release_tree(self, base_dir, files):
        sdist_orig.make_release_tree(self, base_dir, files)
        with open(os.path.join(base_dir, 'setup.json'), 'w') as f:
            json.dump(conf, f)


class features(Command):

    description = 'list features'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        apps, base_addons, extra_addons = analyze()
        features = ['base']
        
        g = defaultdict(set)
        for app in apps:
            g[app] = apps[app].get('app_dependencies')
        
        features += list(topological_sort(g))
        features += ['extra', 'addons']

        for feature in features:
            print(feature)


setup(
    url='https://github.com/odooku/odooku-odoo',
    author='Raymond Reggers - Adaptiv Design',
    license='LGPLv3',
    zip_safe=False,
    cmdclass= {
        'features': features,
        'sdist': sdist
    },
    python_requires='>=3.5',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    ],
    **conf
)
