#!/usr/bin/env python
# -*- coding: utf-8 -*-*
###############################################################################
# Copyright (c) 2017-2021 UCit SAS
# All Rights Reserved
#
# This software is the confidential and proprietary information
# of UCit SAS ("Confidential Information").
# You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of
# the license agreement you entered into with UCit.
###############################################################################
"""HEROES Outpost Worker docstring

This program is part of the HEROES Outpost infrastructure.
It reads messages from RabbitMQ queue and execute workflows commands.

"""
import json
import sys
import os
import subprocess
import yaml

def listen_workflow(**data):
    """
    Function to submit a workflow
    """
    try:
        print("   ----> [x] Worker: Workflow start submission")
        nextflow_build_cmd = [
            "/etc/nextflow/launch.sh",
            "cancel",
            data['instance_id']
        ]
        nextflow_cmd = ' '.join(nextflow_build_cmd)
        # print(nextflow_cmd)
        # workflowResponse = subprocess.Popen(nextflow_build_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        workflowResponse = subprocess.run(nextflow_build_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(workflowResponse.stdout)
        # Show responses with filters

        print("   ----> [x] Worker: Workflow submitted")
        return "done"

    except Exception as e:
        raise


if __name__ == '__main__':
    """
    Main function for workflow listener
    """

    print("   ----> [x] Worker: Start workflow listener")
    body = sys.argv[1]
    print(body)
    data = json.loads(body)
    print(data)

    responseWorkflow = listen_workflow(**data)
    print(responseWorkflow)

    print("   ----> [x] Worker: End workflow listener")
