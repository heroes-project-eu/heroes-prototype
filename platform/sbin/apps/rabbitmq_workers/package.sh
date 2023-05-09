#!/bin/bash


rabbitmq_worker=$1
version="0.2"


rabbitmq_workers_script=$(readlink -f "$0")
rabbitmq_workers_path=$(dirname "$rabbitmq_workers_script")


tar zcvf "${rabbitmq_workers_path}/../../containers/rabbitmq/src/worker/heroes-rabbitmq-${version}.tar.gz" -C "${rabbitmq_workers_path}/${rabbitmq_worker}" .
cp -r "${rabbitmq_workers_path}/${rabbitmq_worker}/playbooks/" "${rabbitmq_workers_path}/../../containers/rabbitmq/src/"
