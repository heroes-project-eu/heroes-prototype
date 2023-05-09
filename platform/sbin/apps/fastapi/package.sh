#!/bin/bash


fastapi=$(readlink -f "$0")
fastapi_path=$(dirname "$fastapi")


version="0.3"
tar zcvf "${fastapi_path}/../../containers/fastapi/src/heroes-fastapi-${version}.tar.gz" -C "${fastapi_path}" .
