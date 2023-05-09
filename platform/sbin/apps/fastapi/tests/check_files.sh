#!/usr/bin/env bash
################################################################################
# Copyright (c) 2017-2021 UCit SAS
# All Rights Reserved
#
# This software is the confidential and proprietary information
# of UCit SAS ("Confidential Information").
# You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of
# the license agreement you entered into with UCit.
################################################################################
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
backpwd="${PWD}"

rv=0

cd_prev_dir() {
  cd "${backpwd}" || return
}

trap cd_prev_dir SIGINT SIGTERM SIGUSR1 SIGUSR2

cd "${DIR}" || exit 1

# Run flake8 on all .py files in fastapi
echo "# Checking .py scripts with flake8"
find "${DIR}/../" -iname '*.py' -print0 | xargs -0 flake8
scrv=$?
if [ ${scrv} -ne 0 ]; then
  rv=$((rv+1))
fi
echo ""

shopt -s globstar nullglob

exit ${rv}
