#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
#
# initializes the venv for the project in the current
# directory. installs poetry in that env for dep mgmt
# and then installs deps using poetry.
##
set -eo pipefail
if [[ "$PYTHON_VERSION" != "" ]]; then
    PYPATH=`which python$PYTHON_VERSION`
else
    PYPATH="python3"
fi
$PYPATH -m venv --prompt "pUnit" .venv
source .venv/bin/activate
pip install poetry
if [ -e pyproject.toml ]; then
    poetry install --no-root
fi
deactivate
