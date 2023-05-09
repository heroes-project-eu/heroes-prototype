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

# Vars
KEYCLOAK_URL=$1
KEYCLOAK_PORT=$2
ORGANIZATION_NAME=$3
ORGANIZATION_CLIENT_ID=$4
ORGANIZATION_CLIENT_SECRET=$5
MINIO_SERVER_URL=$6
MINIO_SERVER_PORT=$7
MINIO_SERVER_CONSOLE_PORT=$8
TEMPLATES_DIR="/opt/heroes/platform/sbin/templates"
MINIO_CONF_DIR="/data/.minio.sys/config"

# Copy the minio.service
mkdir -p /data/.minio.sys/config/
# Template the minio config for the organization
sed -e "s/{{ KEYCLOAK_URL }}/$KEYCLOAK_URL/g" \
    -e "s/{{ KEYCLOAK_PORT }}/$KEYCLOAK_PORT/" \
    -e "s/{{ ORGANIZATION_NAME }}/$ORGANIZATION_NAME/g" \
    -e "s/{{ ORGANIZATION_CLIENT_ID }}/$ORGANIZATION_CLIENT_ID/g" \
    -e "s/{{ ORGANIZATION_CLIENT_SECRET }}/$ORGANIZATION_CLIENT_SECRET/g" \
    -e "s/{{ MINIO_SERVER_URL }}/$MINIO_SERVER_URL/g" \
    -e "s/{{ MINIO_SERVER_CONSOLE_PORT }}/$MINIO_SERVER_CONSOLE_PORT/g" \
    "${TEMPLATES_DIR}/config.json.j2" > "${MINIO_CONF_DIR}/config.json"


mkdir -p "${MINIO_CONF_DIR}/iam/policies/userPolicy/"
cp "${TEMPLATES_DIR}/userPolicy.json" "${MINIO_CONF_DIR}/iam/policies/userPolicy/policy.json"
chown -R minio:minio "${MINIO_CONF_DIR}"


# Start minio-server
minio server /data --address "0.0.0.0:${MINIO_SERVER_PORT}" --console-address "0.0.0.0:${MINIO_SERVER_CONSOLE_PORT}" &
minio_pid=$!
sleep 2


# Wait for any process to exit
wait $minio_pid
exit_pid=$?

# Exit with status of process that exited first
exit $exit_pid
