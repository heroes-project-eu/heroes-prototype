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

# Container arguments
worker_name=$1
echo "worker_name: ${worker_name}" > /tmp/container.args.log
RABBITMQ_DIR="/opt/rabbitmq"


# Start rabbitmq-server
/usr/sbin/rabbitmq-server &
sleep 10

echo "Add: RabbitMQ use and password tuple"
rabbitmqctl add_user 'heroes_fastapi' 'xxxx' 
rabbitmqctl set_user_tags 'heroes_fastapi' administrator
rabbitmqctl set_permissions -p / heroes_fastapi ".*" ".*" ".*"

if [[ "${worker_name}" == "minio" ]]; then
  git config --global user.email "rabbitmq@heroes-project.eu"
  git config --global user.name "RabbitMQ-Worker"
  mkdir ~/.ssh
  ssh-keyscan -H gitlab.doit.priv >> ~/.ssh/known_hosts
  chmod 600 "${RABBITMQ_DIR}/keys/gitlab.key"
fi

mkdir /efs
mkdir /efs/work
mkdir ~/.ssh

# Start worker-server
echo "Start: RabbitMQ worker"
python3.8 "${RABBITMQ_DIR}/worker/worker.py"
worker_pid=$!


# Wait for any process to exit
wait $worker_pid
exit_pid=$?


# Exit with status of process that exited first
exit $exit_pid
