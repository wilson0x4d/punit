#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##
set -eo pipefail
source .venv-bash/bin/activate
sed "s/0.0.0/$SEMVER/g" --in-place pyproject.toml
sed "s/0.0.0/$SEMVER/g" --in-place src/__init__.py
if [ -d ./punit ]; then
  rm ./punit
fi
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
ln -s ./src ./punit
python3 -m build
#python3 -m twine upload --repository $PYPI_REPO dist/*
