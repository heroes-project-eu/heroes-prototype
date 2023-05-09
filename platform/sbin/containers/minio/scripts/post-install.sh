#!/bin/bash
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

echo "**** HEROES Post-Install - START ****"

anspb () {
  anslogfile_basename=$(basename "$1" .yaml)
  anslogfile="/var/log/heroes.${anslogfile_basename}.log"
  touch "${anslogfile}"
  chmod -v 600 "${anslogfile}"
  echo "Running playbook $1 - outputs will be written to ${anslogfile}"
  ansible-playbook -v "$1" > "${anslogfile}" 2>&1
}

anspb "playbooks/install-minio-all.yml"

echo "**** HEROES Post-Install - END ****"
