#!/bin/bash


build=$(readlink -f "$0")
container_path=$(dirname "$build")


docker build -t gitlab.doit.priv:5050/heroes/k8s-apps/minio-server:latest "${container_path}"
docker push gitlab.doit.priv:5050/heroes/k8s-apps/minio-server:latest
