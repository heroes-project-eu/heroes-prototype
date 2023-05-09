#!/bin/bash


build=$(readlink -f "$0")
container_path=$(dirname "$build")


cp "${container_path}/../../apps/fastapi/.env_din" "${container_path}/../../apps/fastapi/.env"
"${container_path}/../../apps/fastapi/package.sh"

docker build -t gitlab.doit.priv:5050/heroes/k8s-apps/fastapi-server:latest "${container_path}"
docker push gitlab.doit.priv:5050/heroes/k8s-apps/fastapi-server:latest
