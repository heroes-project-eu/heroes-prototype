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
import pandas as pd
import re

def listen_workflow(**data):
    """
    Function to monitor a workflow
    """
    try:
        fields = "native_id,task_id,name,process,cpus,time,memory,exit,start,status,submit,rss,queue,read_bytes,write_bytes,pcpu,pmem"
        splitted_fields = fields.split(",")
        nextflow_columns = [fields.split(",")]
        # print(nextflow_columns)
        # print("   ----> [x] Worker: Workflow monitoring START")

        # print("UPDATE n")
        # print(f"Workflow instance id : {data['instance_id']}")
        nextflow_wiid_log_cmd = [
            "/etc/nextflow/launch.sh",
            "log",
            data['instance_id'],
            "-fields",
            fields
        ]
        nextflow_cmd = ' '.join(nextflow_wiid_log_cmd)
        # print(nextflow_cmd)

        workflowResponse = subprocess.run(nextflow_wiid_log_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = workflowResponse.stdout

        nextflow_tasks = []
        if output:
            # print(output)
            if "no pipeline" not in str(output):
                # print("### IN OUTPUT ###")
                output_data = output.decode("utf-8").split("\n")
                # print(output_data)
                for current_task in output_data:
                    if current_task:

                        parsed_task = {}
                        splitted_task = current_task.split("\t")

                        for data_index in range(0,len(fields.split(","))):
                            parsed_task[splitted_fields[data_index]] = splitted_task[data_index]

                        if int(parsed_task["cpus"]) != 0 and re.match(r'^-?\d+(?:\.\d+)$', parsed_task["pcpu"].rstrip("%")) is not None:
                            parsed_task["cpu_used"] = int(parsed_task["cpus"]) * float(parsed_task["pcpu"].rstrip("%"))/100
                        else:
                            parsed_task["cpu_used"] = 0

                        if int(parsed_task["memory"].split(" ")[0]) != 0 and re.match(r'^-?\d+(?:\.\d+)$', parsed_task["pmem"].rstrip("%")) is not None:
                            parsed_task["mem_used"] = int(parsed_task["memory"].split(" ")[0]) * float(parsed_task["pmem"].rstrip("%"))/100
                        else:
                            parsed_task["mem_used"] = 0

                        nextflow_tasks.append(parsed_task)

        return nextflow_tasks

    except Exception as e:
        raise


if __name__ == '__main__':
    """
    Main function for workflow listener
    """

    # print("   ----> [x] Worker: Start workflow listener")
    body = sys.argv[1]
    # print(body)
    data = json.loads(body)
    # print(data)

    responseWorkflow = listen_workflow(**data)
    print(responseWorkflow)

    # print("   ----> [x] Worker: End workflow listener")
