#!/bin/bash
# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
##
set -eo pipefail
source .venv-bash/bin/activate
python -m src -a punit src -a punit.facts src.facts --report html --output results.html
