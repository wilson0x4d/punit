#!/bin/pwsh
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
#
# initializes the venv for the project in the current
# directory, including performing initial dependency
# installation.
##
$ErrorActionPreference = "Stop"
if ($env:PYTHON_VERSION -ne "") {
    $PYPATH=$(Get-Command "python$env:PYTHON_VERSION").Source
} else {
    $PYPATH=$(Get-Command "python3").Source
}
& $PYPATH -m venv --prompt "pUnit" .venv-pwsh
. .\.venv-pwsh\Scripts\Activate.ps1
& pip install --upgrade pip
& pip install pip-tools
& pip-compile -o requirements.txt --all-extras --strip-extras pyproject.toml
& python -m pip install -r requirements.txt
