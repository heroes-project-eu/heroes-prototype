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
import pika
import json
import os
import subprocess


RABBITMQ_DIR="/opt/rabbitmq"


def on_request(ch, method, properties, body):
    """
    Function that is invoked every time a new message is
    found in the relative RabbitMQ queue
    """

    print("   --> [x] Worker: Message received")
    data = json.loads(body)

    workflow_action = [
        "python3.8",
        f"{RABBITMQ_DIR}/worker/workflow_{data['action']}.py",
        body
    ]
    # print(workflow_action)

    print(data)
    print("START ACTION")

    response=""
    if data["action"] == "executor":
        workflowResponse = subprocess.Popen(workflow_action, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # workflowResponse = subprocess.run(workflow_action, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # print(workflowResponse.stdout)
        response = "done"
    elif data["action"] == "listener":
        workflowResponse = subprocess.run(workflow_action, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(workflowResponse.stdout)
        response = workflowResponse.stdout
    elif data["action"] == "delete":
        workflowResponse = subprocess.run(workflow_action, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(workflowResponse.stdout)
        response = workflowResponse
        # response = workflowResponse.decode("utf-8")

    print("END ACTION")
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id = properties.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(' [*] Waiting for new messages. To exit press CTRL+C')


if __name__ == '__main__':

    rabbitmq_host = "localhost"
    credentials = pika.PlainCredentials('heroes_fastapi', 'xxxx')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host,
            port=5672,
            heartbeat=60,
            connection_attempts=5,
            retry_delay=1,
            credentials=credentials))

    channel = connection.channel()
    channel.queue_declare(queue='worker_workflow_queue')
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='worker_workflow_queue',
        on_message_callback=on_request
    )
    channel.start_consuming()
