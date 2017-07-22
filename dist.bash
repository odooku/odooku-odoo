#!/usr/bin/env bash

source version

# sdist odoo
echo "Running sdist for Odoo"
ODOO_VERSION=$ODOO_VERSION ODOO_URL=$ODOO_URL python setup.py sdist &> /dev/null

# sdist features
features=($(ODOO_VERSION=$ODOO_VERSION python setup.py features))
for f in "${features[@]:2}"; do
echo "Running sdist for feature $f"
ODOO_VERSION=$ODOO_VERSION FEATURE=$f python setup.py sdist &> /dev/null
done