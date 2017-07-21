#!/usr/bin/env bash

ODOO_VERSION=10.0.0

# sdist odoo
ODOO_VERSION=$ODOO_VERSION python setup.py sdist

# sdist features
features=($(ODOO_VERSION=$ODOO_VERSION python setup.py features))
for f in "${features[@]:2}"; do
echo "Running sdist for feature $f"
ODOO_VERSION=$ODOO_VERSION FEATURE=$f python setup.py sdist
done