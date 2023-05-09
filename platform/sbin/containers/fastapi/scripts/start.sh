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

# Start fastapi-server
uvicorn main:app --host 0.0.0.0 --port 80 --app-dir /opt/fastapi &
fastapi_pid=$!

# Wait for any process to exit
wait $fastapi_pid
exit_pid=$?

# Exit with status of process that exited first
exit $exit_pid
