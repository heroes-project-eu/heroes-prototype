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
from jinja2 import FileSystemLoader, Environment
import tempfile


def prepare_cluster(**data):
    """
    Function to make the deployments
    """
    try:
        print(data)
        print("   ----> [x] Worker: Prepare deployment")

        # Generate the yaml
        organization_yaml = yaml.dump(
            data["organization"],
            explicit_start=True,
            indent=2
        )
        # sort_keys=False.

        print(organization_yaml)

        tmpOrganization = tempfile.NamedTemporaryFile(suffix='.yml')
        with open(tmpOrganization.name, 'w') as organization_file:
            organization_file.write(organization_yaml)

        for currentTask in data['workflow']['tasks']:
            ansibleConfig = tempfile.NamedTemporaryFile()
            with open(ansibleConfig.name, 'w') as config_file:
                config_file.write("[mockup]\n")
                config_file.write(data['workflow']['tasks'][currentTask]['cluster']['address'])

            playbookDir = '/opt/rabbitmq/deployment/ansible'
            playbook = playbookDir + '/main.yml'

            print(f"   ----> [x] Worker: Deployment over cluster {data['workflow']['tasks'][currentTask]['cluster']['name']}")

            execAnsible = subprocess.run([
                "ansible-playbook",
                "--private-key",
                data['workflow']['tasks'][currentTask]['cluster']['ssh_path'],
                "-u",
                data['workflow']['tasks'][currentTask]['cluster']['user'],
                "-i",
                ansibleConfig.name,
                "-v",
                playbook,
                "--ssh-extra-args",
                f"'-o StrictHostKeyChecking=no' -p {str(data['workflow']['tasks'][currentTask]['cluster']['port'])}",
                "--extra-vars",
                "@" + tmpOrganization.name
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            print(execAnsible.stdout)
        print("   ----> [x] Worker: Deployment done")
        return "done"
    except Exception as e:
        raise

def submit_workflow(**data):
    """
    Function to submit a workflow
    """
    try:
        print("   ----> [x] Worker: Launch workflow")

        # Todo: delete after test
        user_work_dir = "/efs/work"
        for currentTask in data['workflow']['tasks']:
            user_work_dir = data['workflow']['tasks'][currentTask]['cluster']['work_dir']

        print("WORK DIR: user_work_dir")

        HEROES_JSON_VARIABLES = {
            "HEROES_ORGANIZATION_ID": data['organization']['organization'][0]['uuid'],
            "HEROES_ORGANIZATION_NAME": data['organization']['organization'][0]['name'],
            "HEROES_USER_ID": data['organization']['organization'][0]['users'][0]['uuid'],
            "HEROES_WORKFLOW_ID": data['workflow']['id'],
            "HEROES_WORKFLOW_INSTANCE_ID": data['workflow']['instance_id'],
            "HEROES_USER_WORKDIR": f"{user_work_dir}/{data['organization']['organization'][0]['uuid']}/{data['organization']['organization'][0]['users'][0]['uuid']}/{data['workflow']['id']}/{data['workflow']['instance_id']}",
            "HEROES_LOGS_PATH": f"{user_work_dir}/{data['organization']['organization'][0]['uuid']}/{data['organization']['organization'][0]['users'][0]['uuid']}/{data['workflow']['id']}/{data['workflow']['instance_id']}"
        }
        var_count = 0
        HEROES_VARIABLES = ""
        for current_heroes_var in HEROES_JSON_VARIABLES:
            if var_count == 0:
                HEROES_VARIABLES = f'{current_heroes_var}="{HEROES_JSON_VARIABLES[current_heroes_var]}"'
            else:
                HEROES_VARIABLES = f'{HEROES_VARIABLES},{current_heroes_var}="{HEROES_JSON_VARIABLES[current_heroes_var]}"'
            var_count = var_count + 1
        print(HEROES_VARIABLES)
        # Load the j2 template of nextflow config
        HEROES_DIR = "/opt/rabbitmq/"
        file_loader = FileSystemLoader(f"{HEROES_DIR}/templates/")
        env = Environment(loader=file_loader)

        # Bind the variables for the template rendering
        template = env.get_template("rclone.config.j2")
        rcl_file = template.render(
            TASKS=data['workflow']['tasks'],
            DATA=data['workflow']['data'],
            ORGANIZATION=data['organization']['organization'][0]['name']
        )
        RCloneConfigFile = tempfile.NamedTemporaryFile(suffix='.config')
        with open(RCloneConfigFile.name, 'w') as RClCoFile:
            RClCoFile.write(rcl_file)

        with open(RCloneConfigFile.name, 'r') as f:
            file_contents = f.read()
        print(file_contents)

        # Bind the variables for the template rendering
        EAR_DIRECTORY = "/home/hsuser/ear"
        template = env.get_template("workflow.config.j2")
        print(data['workflow']['tasks'])
        yml_file = template.render(
            TASKS=data['workflow']['tasks'],
            DATA=data['workflow']['data'],
            RCLONE_CONFIG_FILE=RCloneConfigFile.name,
            ORGANIZATION=data['organization']['organization'][0]['name'],
            WORK_DIRECTORY=HEROES_JSON_VARIABLES["HEROES_USER_WORKDIR"],
            EAR_DIRECTORY="/home/hsuser/ear",
            EAR_SINGULARITY_DIRECTORY="/hpc/ear",
            BUCKET=data['organization']['organization'][0]['users'][0]['name'],
            HEROES_VARIABLES=HEROES_VARIABLES
        )
        nextflowConfigFile = tempfile.NamedTemporaryFile(suffix='.config')
        with open(nextflowConfigFile.name, 'w') as nxtCoFile:
            nxtCoFile.write(yml_file)

        with open(nextflowConfigFile.name, 'r') as f:
            file_contents = f.read()
        print(file_contents)

        print("   ----> [x] Worker: Workflow start submission")
        print(f"rclone copy {data['organization']['organization'][0]['name']}:{data['workflow']['script']} {HEROES_JSON_VARIABLES['HEROES_USER_WORKDIR']} --config RCloneConfigFile.name")
        rclone_transfer = subprocess.run([
            "rclone",
            "copy",
            f"{data['organization']['organization'][0]['name']}:{data['workflow']['script']}",
            f"{HEROES_JSON_VARIABLES['HEROES_USER_WORKDIR']}",
            "--config",
            RCloneConfigFile.name
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(rclone_transfer.stdout)

        nextflow_build_cmd = [
            "/etc/nextflow/launch.sh",
            "-log",
            "/var/log/nextflow.log",
            "run",
            f"{HEROES_JSON_VARIABLES['HEROES_USER_WORKDIR']}/{data['workflow']['script'].split('/')[-1]}",
            "-name",
            data['workflow']['instance_id'],
            "-w",
            HEROES_JSON_VARIABLES['HEROES_USER_WORKDIR'],
            "-c",
            nextflowConfigFile.name,
            "-with-trace",
            "-profile",
            "singularity"
        ]
        nextflow_cmd = ' '.join(nextflow_build_cmd)
        print(nextflow_cmd)
        # workflowResponse = subprocess.Popen(nextflow_build_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        workflowResponse = subprocess.run(nextflow_build_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(workflowResponse.stdout)

        # sleep(5)
        # for nextflow_listener_calls in range(0,5):
        #     print(f"CALL LOG n°{nextflow_listener_calls}")
        #     nextflow_build_cmd = [
        #         "/etc/nextflow/launch.sh",
        #         "log",
        #     ]
        #     nextflow_cmd = ' '.join(nextflow_build_cmd)
        #     print(nextflow_cmd)
        #     workflowResponse = subprocess.run(nextflow_build_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #     print(workflowResponse.stdout)
        #     sleep(3)

        print("   ----> [x] Worker: Workflow submitted")
        return "done"

    except Exception as e:
        raise


if __name__ == '__main__':
    """
    Main function for workflow execution
    """

    print("   ----> [x] Worker: Start workflow executor")
    body = sys.argv[1]
    print(body)
    data = json.loads(body)
    print(data)

    responseCluster = prepare_cluster(**data)
    print(responseCluster)
    responseWorkflow = submit_workflow(**data)
    print(responseWorkflow)

    print("   ----> [x] Worker: End workflow executor")
