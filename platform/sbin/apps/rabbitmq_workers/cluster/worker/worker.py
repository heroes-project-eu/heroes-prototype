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
It reads messages from RabbitMQ queue and execute cluster commands.

"""
import pika
import json
import os
import shutil
from git import Repo, Git
from jinja2 import FileSystemLoader, Environment


RABBITMQ_DIR="/opt/rabbitmq"


def aws_pcluster(**data):
    """
    Function to interact with aws parallelcluster
    """
    print("   ----> [x] Worker: Get information about " + data['organization'])
    # Todo: Request client id & secret from db? or pass it?
    # Check if the organization exists
    print(f"   ----> [x] Worker: MinIO server {data['action']} operation... ")

    if data['action'] == "create":
        try:
            # pcluster create -nr -nw data['cluster_name']
            pass
        except Exception as e:
            raise e
    elif data['action'] == "delete":
        try:
            # pcluster delete -nw data['cluster_name']
            pass
        except Exception as e:
            raise e

    print("   --> [x] Worker: AWS PCLUSTER operation done")
    return "done"


def call_response(cluster_name, cluster_status):
    # Todo: Connexion ? Service account in master org?
    data = {
        "organization": organization_name,
        "cluster": cluster_name,
        "status": server_status
    }
    headers = {
        "Authorization": "Bearer " + token['access_token'],
        "Content-Type": "application/json"
    }
    return requests.post(
        f"{}://fastapi-server{}" \
        + f"/heroes/admin/organizations/{organization_id}/clusters",
        data=json.dumps(data),
        headers=headers
    )


def callback(ch, method, properties, body):
    """
    Function that is invoked every time a new message is
    found in the relative RabbitMQ queue
    """

    print("   --> [x] Worker: Received and Deserialize")
    data = json.loads(body)
    data['organization'] = data['organization'].lower()
    print("   --> [x] Worker: Action X for {}".format(data['organization']))

    if data['organization'] == "aws":
        response = aws_pcluster(**data)
    if response == "done":
        pass
        # call_response(cluster_name, cluster_status)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(' [*] Waiting for new messages. To exit press CTRL+C')


if __name__ == '__main__':
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='worker_cluster_queue', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='worker_cluster_queue',
        on_message_callback=callback
    )
    channel.start_consuming()
