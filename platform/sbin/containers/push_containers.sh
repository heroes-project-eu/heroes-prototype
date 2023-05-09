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

build=$(readlink -f "$0")
containers_path=$(dirname "$build")
containers=$(ls -l | grep "^d" | awk '{print $9}')
for container in ${containers}; do
  if [[ "${container}" != "README.md" ]]; then
    echo "Build && push: ${container}"
    echo "${containers_path}/${container}"
    "${containers_path}/${container}/build.sh"
    echo "Build && push: done"
  fi
done
