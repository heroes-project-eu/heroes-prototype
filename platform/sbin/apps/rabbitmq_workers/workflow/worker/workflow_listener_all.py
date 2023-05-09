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
    Function to submit a workflow
    """
    try:
        fields = "native_id,task_id,name,hash,process,cpus,time,memory,exit,start,status,submit,rss,queue,read_bytes,write_bytes,pcpu,pmem"
        nextflow_columns = [fields.split(",")]
        # print(nextflow_columns)

        print("   ----> [x] Worker: Workflow start submission")
        nextflow_build_cmd = [
            "/etc/nextflow/launch.sh",
            "log"
        ]
        # nextflow_cmd = ' '.join(nextflow_build_cmd)
        # print(nextflow_cmd)

        workflowResponse = subprocess.run(nextflow_build_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = workflowResponse.stdout

        # splitting the output so that
        # we can parse them line by line
        output = output.decode("utf-8")
        output = output.split("\n")
        # print(output)
        for current_output in output[1:-1]:
            print("UPDATE 1")
            print(current_output)
            workflow_instance_id = f"wiid-{current_output.split('wiid-')[1].split(' ')[0]}"
            print(f"Workflow instance id : {workflow_instance_id}")
            nextflow_wiid_log_cmd = [
                workflow_instance_id,
                "-fields",
                fields
            ]
            nextflow_cmd = ' '.join(nextflow_build_cmd+nextflow_wiid_log_cmd)
            print(nextflow_cmd)

            workflowResponse = subprocess.run(nextflow_build_cmd+nextflow_wiid_log_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = workflowResponse.stdout

            if output:
                print("### IN OUTPUT ###")
                output_data = output.decode("utf-8").split("\n")
                print(output_data)
                nextflow_tasks = []
                for current_task in output_data:
                    if current_task:
                        nextflow_tasks.append(current_task.split("\t"))
                        print(current_task.split("\t"))

                df = pd.DataFrame(nextflow_tasks , columns=nextflow_columns)

                cpu_used = []
                mem_used = []
                # df["memory"] = df["memory"].replace(["-"],[0])

                print("### ROW ###")
                for index, row in df.iterrows():
                    # print(row)
                    if int(row["cpus"][0]) !=0 and re.match(r'^-?\d+(?:\.\d+)$', row["pcpu"][0].rstrip("%")) is not None:
                        cpu = int(row["cpus"][0]) * float(row["pcpu"][0].rstrip("%"))/100
                    else:
                        cpu = 0

                    cpu_used.append(cpu)

                    if int(row["memory"][0].split(" ")[0]) != 0 and re.match(r'^-?\d+(?:\.\d+)$', row["pmem"][0].rstrip("%")) is not None:
                        mem = int(row["memory"][0].split(" ")[0]) * float(row["pmem"][0].rstrip("%"))/100
                    else:
                        mem = 0

                    mem_used.append(mem)

                df["cpu_used"] = cpu_used
                df["mem_used"] = mem_used
                print(df)

        print("   ----> [x] Worker: Workflow submitted")
        return "ok"
        # return df

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
