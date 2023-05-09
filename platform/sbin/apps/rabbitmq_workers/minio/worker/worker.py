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
It reads messages from RabbitMQ queue and execute server starts.

"""
import pika
import json
import os
import shutil
from git import Repo, Git
from jinja2 import FileSystemLoader, Environment


RABBITMQ_DIR="/opt/rabbitmq"


def minio_server(**data):
    """
    Function to start/delete a minio server within kubernetes
    """
    print("   ----> [x] Worker: Get information about " + data['organization'])
    # Todo: Request client id & secret from db? or pass it?
    # Check if the organization exists
    print(f"   ----> [x] Worker: MinIO server {data['action']} operation... ")
    ORG_DIR = f"{RABBITMQ_DIR}/minio/k8s-apps/minio-server/" \
        + f"{data['organization']}"
    REPO_DIR = f"{RABBITMQ_DIR}/minio/k8s-apps"
    # Retrieve the k8s-apps git
    k8s_apps = "git@gitlab.doit.priv:heroes/k8s-apps.git"
    git_ssh_identity_file = os.path.expanduser(
        f"{RABBITMQ_DIR}/keys/gitlab.key")
    git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        if os.path.isdir(REPO_DIR):
            repo = Repo(REPO_DIR)
            repo.git.pull('origin')
        else:
            Repo.clone_from(
                k8s_apps,
                REPO_DIR,
                env={"GIT_SSH_COMMAND": f"{git_ssh_cmd}"}
            )

    if data['action'] == "create":
        # Create the branch directory for the organization
        try:
            os.makedirs(ORG_DIR)
        except OSError:
            if not os.path.isdir(ORG_DIR):
                raise
        for k8s_file in "deployment", "service":  # Todo: Vars?
            # Load the j2 template of the k8s_file
            file_loader = FileSystemLoader(f"{RABBITMQ_DIR}/templates/")
            env = Environment(loader=file_loader)
            template = env.get_template(f"{k8s_file}.yml.j2")
            # Bind the variables for the template rendering
            render_template = template.render(
                KEYCLOAK_URL="keycloak-server.heroes.svc.cluster.local",  # Todo: Var?
                KEYCLOAK_PORT="8080",  # Todo: Var?
                ORGANIZATION_NAME=data['organization'],
                ORGANIZATION_CLIENT_ID=data['client'],
                ORGANIZATION_CLIENT_SECRET=data['secret'],
                MINIO_SERVER_URL="minio-server-" + data['organization'] + ".heroes.svc.cluster.local",
                MINIO_SERVER_PORT="9000",  # Todo: Var?
                MINIO_SERVER_CONSOLE_PORT="9001"  # Todo: Var?
            )

            with open(f"{ORG_DIR}/{k8s_file}.yml", 'w') as yml_file:
                yml_file.write(render_template)
    elif data['action'] == "delete":
        try:
            # Delete the branch directory for the organization
            if os.path.exists(ORG_DIR):
                shutil.rmtree(ORG_DIR)
        except OSError:
            if os.path.isdir(ORG_DIR):
                raise

    # Push the modifications
    try:
        with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
            repo = Repo(REPO_DIR)
            repo.git.add(ORG_DIR)
            commit_msg = f"{data['action']}: " \
                + f"{data['organization'].lower()} minio server"
            repo.git.commit('-m', commit_msg)  # Todo: change
            repo.git.push('origin', env={"GIT_SSH_COMMAND": f"{git_ssh_cmd}"})
    except Exception as e:
        raise e
        print("error")

    print("   --> [x] Worker: MinIO server operation done")
    return "done"


# def call_response(server_name, server_status):
#     # Todo: Connexion ? Service account in master org?
#     data = {
#         "organization": organization_name,
#         "server": server_name,
#         "status": server_status
#     }
#     headers = {
#         "Authorization": "Bearer " + token['access_token'],
#         "Content-Type": "application/json"
#     }
#     return requests.post(
#         f"{}://fastapi-server{}" \
#         + f"/heroes/admin/organizations/{organization_id}/servers",
#         data=json.dumps(data),
#         headers=headers
#     )

def callback(ch, method, properties, body):
    """
    Function that is invoked every time a new message is
    found in the relative RabbitMQ queue
    """

    print("   --> [x] Worker: Received and Deserialize")
    data = json.loads(body)
    data['organization'] = data['organization'].lower()
    print("   --> [x] Worker: Creating MinIO server for {}".format(data['organization']))
    response = minio_server(**data)
    if response == "done":
        pass
        # call_response(f"minio-server-{data['organization']}", "CREATE_IN_PROGRESS")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(' [*] Waiting for new messages. To exit press CTRL+C')


if __name__ == '__main__':
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='worker_minio_queue', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='worker_minio_queue',
        on_message_callback=callback
    )
    channel.start_consuming()
