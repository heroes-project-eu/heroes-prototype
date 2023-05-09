#!/bin/bash


# Vars
fastapi_url="fastapi.heroes.doit.priv"
organization="xxxx"
bucket_name="xxxx"
username="xxxx"
password="xxxx"
file="example.txt"

# Functions
function login() {
  set -x
  curl --insecure -s 'POST' \
  "https://${fastapi_url}/organization/auth/login" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{\"organization\": \"${organization}\", \"username\": \"${username}\", \"password\": \"${password}\"}"
  set +x
}


function user_info() {
  token=$1
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/auth/me" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


function data_list() {
  token=$1
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/data/list" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


function object_list() {
  token=$1
  bucket_name=$2
    # todo: delete / at the end of list
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/data/bucket/${bucket_name}/list" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


function download_file() {
  token=$1
  bucket_name=$2
  file=$3
  set -x
  curl --insecure -o "${file}-downloaded" -s -X 'GET'  \
  "https://${fastapi_url}/organization/data/download?&bucket=${bucket_name}&file=${file}" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
  cat "${file}-downloaded"
}


function upload_file() {
  token=$1
  bucket_name=$2
  file=$3
  local_path=$(pwd)
  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/data/upload?&bucket=${bucket_name}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: multipart/form-data' \
  -F "file=@${local_path}/${file};type=application/octet-stream"
  set +x
}


function list_workflow() {
  token=$1
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/workflow/list" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
  set +x
}


function submit_workflow() {
  token=$1
  workflow_template_id=$2
  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/workflow/submit?workflow_template_id=${workflow_template_id}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json' \
  -d '{ "workflow_name": "jr_workflow", "workflow_input_dir": "/basicuser/wf1-config", "workflow_placement": {"cluster": "cluster2"}, "workflow_parameters": {"SplitLetters": {"cpus": "1"}, "ConvertToUpper": {"cpus": "1"}}}'
  # -d "{\"organization\": \"${organization}\", \"username\": \"${username}\", \"password\": \"${password}\"}"
  set +x
}


function refresh_token() {
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/auth/refresh_token" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


function logout() {
  token=$1
  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/auth/logout" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


clear
echo "### TEST: Login"
response=$(login)
token=$response
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: User info"
response=$(user_info "${token}")
echo "${response}" | jq
read $wait_demo


Data Management part


clear
echo "### TEST: Data list"
response=$(data_list "${token}")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Object list"
response=$(object_list "${token}" "${bucket_name}")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Upload file ${file}"
response=$(upload_file "${token}" "${bucket_name}" "${file}")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Object list"
response=$(object_list "${token}" "${bucket_name}")
# file=$(echo "${response}" .[0].object_name | awk -F'"' '{print $2}')
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Download file ${file}"
response=$(download_file "${token}" "${bucket_name}" "${file}")
echo "${response}"
read $wait_demo


# Workflow part


clear
echo "### TEST: List workflow"
response=$(list_workflow "${token}")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Submit workflow"
response=$(submit_workflow "${token}" "1")
echo "${response}" | jq
read $wait_demo
