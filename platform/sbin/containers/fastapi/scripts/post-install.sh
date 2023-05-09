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
  echo "Running playbook $1"
  ansible-playbook -v "$1"
}

anspb "playbooks/install-fastapi-all.yml"

echo "**** HEROES Post-Install - END ****"
