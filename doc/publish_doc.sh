#!/bin/bash
################################################################################
# Copyright (c) 2017-2022 HEROES SAS
# All Rights Reserved
#
# This software is the confidential and proprietary information
# of HEROES SAS ("Confidential Information").
# You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of
# the license agreement you entered into with HEROES.
################################################################################
# Script to compile and publish HEROES documentation
#
# It is assumed that
# - all prerequisites for sphinx are installed
# - AWS CLI is installed and configured to access the bucket

DOC_S3_BUCKET="HEROES-documentation"
BUILD_DIR="build"
EXCLUDES=( _sources .buildinfo .doctrees )
REQS=(sphinx-build aws)

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPTDIR}" || exit

echo "###############################################################"
echo "### Building HEROES Documentation..."

# Check that we have the mandatory requirements
for req in "${REQS[@]}"; do
  if ! command -v "${req}" >/dev/null ; then
    echo "Missing requirement: '${req}'... Exiting"
    exit 1
  fi
done


# 1. cleanup existing build directory
# 2. generate doc
rm -rf "${BUILD_DIR}"
sphinx-build -b html ./HEROES/ "${BUILD_DIR}"
rv=$?
if [[ "${rv}" != 0 ]]; then
  echo "An error occured while building the documentation. It will not be synchronized with AWS... Exiting"
  exit 1
fi
echo "### HEROES Documentation built in \"${BUILD_DIR}/\""

# 3. Delete files/directories to exclude: this is much easier than managing correctly the patterns with aws s3 sync --exclude
for exc in "${EXCLUDES[@]}"; do
  rm -rf "${BUILD_DIR:?}/${exc}"
done

# 4. push to remote s3 bucket
echo "### Synching documentation with s3://${DOC_S3_BUCKET}/"
aws s3 sync --delete "${BUILD_DIR}/" "s3://${DOC_S3_BUCKET}/"

echo "### All done"
echo "###############################################################"
