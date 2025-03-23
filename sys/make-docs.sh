#!/bin/bash
# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
set -eo pipefail
source .venv-bash/bin/activate
if [[ "$1" == "" ]]; then
    pip install sphinx_rtd_theme
fi
cd docs/
make html
