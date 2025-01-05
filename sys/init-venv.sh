#!/bin/bash
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
#
# initializes the venv for the project in the current
# directory, including performing initial dependency
# installation.
##
set -eo pipefail
if [[ "$PYTHON_VERSION" != "" ]]; then
    PYPATH=`which python$PYTHON_VERSION`
else
    PYPATH="python3"
fi
$PYPATH -m venv --prompt "pUnit" .venv-bash
source .venv-bash/bin/activate
pip install -r requirements-dev.txt
deactivate
