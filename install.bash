#!/usr/bin/env bash

source version

# install odoo
echo "Installing Odoo"
pip install ./dist/odooku-odoo-$ODOO_VERSION.tar.gz &> /dev/null

# install features
features=($(ODOO_VERSION=$ODOO_VERSION python setup.py features))
for f in "${features[@]:2}"; do
echo "Installing feature $f"
pip install ./dist/odooku-odoo-$f-$ODOO_VERSION.tar.gz &> /dev/null
done