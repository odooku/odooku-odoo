#!/usr/bin/env bash

python setup.py clean --all

# bdist_wheel features
features=($(python setup.py features))
for f in "${features[@]:2}"; do
echo "Running bdist_wheel for feature $f"
FEATURE=$f python setup.py bdist_wheel &> /dev/null
python setup.py clean --all
done