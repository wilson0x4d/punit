#!/bin/bash
# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
##
set -eo pipefail
source .venv-bash/bin/activate
sed "s/0.0.0/$SEMVER/g" --in-place pyproject.toml
sed "s/0.0.0/$SEMVER/g" --in-place punit/__init__.py
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
python3 -m build
python3 -m twine upload --repository $PYPI_REPO dist/*
