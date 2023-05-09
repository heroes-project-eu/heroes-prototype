#!/bin/bash


build=$(readlink -f "$0")
container_path=$(dirname "$build")


for rabbitmq_worker in $(ls -l "${container_path}/../../apps/rabbitmq_workers" | grep '^d' | awk -F' ' '{print $9}'); do

  if [[ -d "${container_path}/src/worker/" ]]; then
    rm -rf "${container_path}/src/worker/"
    mkdir "${container_path}/src/worker/"
  else
    mkdir "${container_path}/src/worker/"
  fi

  if [[ -d "${container_path}/src/playbooks/" ]]; then
    rm -rf "${container_path}/src/playbooks/"
  fi

  "${container_path}/../../apps/rabbitmq_workers/package.sh" "${rabbitmq_worker}"
  docker build -t "gitlab.doit.priv:5050/heroes/k8s-apps/rabbitmq-worker-${rabbitmq_worker}:latest" "${container_path}"
  docker push "gitlab.doit.priv:5050/heroes/k8s-apps/rabbitmq-worker-${rabbitmq_worker}:latest"

done
