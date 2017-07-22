#!/usr/bin/env bash

source version

# install odoo
pip install ./dist/odooku-odoo-$ODOO_VERSION.tar.gz

# install features
features=($(ODOO_VERSION=$ODOO_VERSION python setup.py features))
for f in "${features[@]:2}"; do
echo "Running sdist for feature $f"
pip install ./dist/odooku-odoo-$f-$ODOO_VERSION.tar.gz
done