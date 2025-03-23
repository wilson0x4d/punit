#!/bin/bash
# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
#
# use this script to drop into a venv.
#
# sys/with-venv.sh
#
##
source ~/.bashrc
export PS1='\$ '
echo -n -e "\033]0;pUnit\007"
bash --rcfile .venv-bash/bin/activate
