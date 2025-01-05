#!/bin/pwsh
# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
#
# enters into a venv shell for the project, intended
# for use by developers. this is simply activating
# the venv, but since i use different toolchains
# for different projects this just helps me keep
# things consistent.
##
pwsh -noe ".\.venv-pwsh\Scripts\Activate.ps1"
