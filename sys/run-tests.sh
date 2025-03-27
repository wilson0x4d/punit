#!/bin/bash
# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
##
set -eo pipefail
source .venv-bash/bin/activate
python -m punit --trait '!integration' --report html --output results.html
