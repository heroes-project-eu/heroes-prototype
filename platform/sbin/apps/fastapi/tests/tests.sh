#!/bin/bash

# Vars
fastapi_url="3.249.68.4:8000"
# organization="xxxx"
# bucket_name="xxxx"
# username="xxxx"
# password='xxxx'


organization="master"
bucket_name="xxxx"
username="xxxx"
password="xxxx"


# Functions
function login() {
  response=$(curl -s -X 'POST' \
  "http://${fastapi_url}/auth/login" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{\"organization\": \"${organization}\", \"username\": \"${username}\", \"password\": \"${password}\"}")
  echo "${response}"
}


function user_info() {
  access_token=$1
  response=$(curl -s -X 'GET' \
  "http://${fastapi_url}/auth/me?organization=${organization}" \
  -H 'accept: application/json' \
  -H "access-token: ${access_token}")
  echo "${response}"
}


function data_list() {
  id_token=$1
  access_token=$2
  response=$(curl -s -X 'GET' \
  "http://${fastapi_url}/data/list?organization=${organization}" \
  -H 'accept: application/json' \
  -H "id-token: ${id_token}" \
  -H "access-token: ${access_token}")
  echo "${response}"
}


function object_list() {
  response=$(curl -s -X 'GET' \
  "http://${fastapi_url}/data/list/objects?organization=${organization}&bucket_name=${bucket_name}" \
  -H 'accept: application/json' \
  -H "id-token: ${id_token}" \
  -H "access-token: ${access_token}")
  echo "${response}"
}


function download_file() {
  file=$1
  curl -o "${file}" -s -X 'GET' \
  "http://${fastapi_url}/data/download?organization=${organization}&bucket=${bucket_name}&file=${file}" \
  -H 'accept: application/json' \
  -H "id-token: ${id_token}" \
  -H "access-token: ${access_token}"
  cat "${file}"
}


function upload_file() {
  file=$1
  local_path=$(pwd)
  response=$(curl -s -X 'POST' \
  "http://${fastapi_url}/data/upload?organization=${organization}&bucket=${bucket_name}" \
  -H 'accept: application/json' \
  -H "id-token: ${id_token}" \
  -H "access-token: ${access_token}" \
  -H 'Content-Type: multipart/form-data' \
  -F "file=@${local_path}/${file};type=application/octet-stream")
  echo "${response}"
}


function refresh_token() {
  response=$(curl -s -X 'GET' \
  "http://${fastapi_url}/auth/refresh_token?organization=${organization}" \
  -H 'accept: application/json' \
  -H "refresh-token: ${refresh_token}" \
  -H "access-token: ${access_token}")
  echo "${response}"
}


function logout() {
  refresh_token=$1
  access_token=$2
  response=$(curl -s -X 'POST' \
  "http://${fastapi_url}/auth/logout?organization=${organization}" \
  -H 'accept: application/json' \
  -H "refresh-token: ${refresh_token}" \
  -H "access-token: ${access_token}" \
  -d "{\"name\": \"${organization}\"}")
  echo "${response}"
}


function create_organization() {
  access_token=$1
  response=$(curl -s -X 'POST' \
  "http://${fastapi_url}/heroes/admin/organization/?organization=${organization}" \
  -H 'accept: application/json' \
  -H "access-token: ${access_token}" \
  -H 'Content-Type: application/json' \
  -d '{"name": "OrganizationTest"}')
  echo "${response}"
}


function get_organization() {
  access_token=$1
  response=$(curl -s -X 'GET' \
  "http://${fastapi_url}/heroes/admin/organizations/${organization}?organization_name=OrganizationTest" \
  -H 'accept: application/json' \
  -H "access-token: ${access_token}")
  echo "${response}"
}


function delete_organization() {
  access_token=$1
  response=$(curl -s -X 'DELETE' \
  "http://${fastapi_url}/heroes/admin/organization/?organization=${organization}&organization_target=OrganizationTest" \
  -H 'accept: application/json' \
  -H "access-token: ${access_token}" \
  -H 'Content-Type: application/json' \
  -d '{"name": "OrganizationTest"}')
  echo "${response}"
}


echo "### TEST: Login"
response=$(login)
echo "${response}" | jq
access_token=$(echo ${response} | jq .access_token | awk -F'"' '{print $2}')
id_token=$(echo ${response} | jq .id_token | awk -F'"' '{print $2}')
refresh_token=$(echo ${response} | jq .refresh_token | awk -F'"' '{print $2}')


echo "### TEST: User info"
response=$(user_info $access_token)
echo "${response}" | jq


# echo "### TEST: Data list"
# response=$(data_list $id_token $access_token)
# echo "${response}" | jq
#
#
# echo "### TEST: Object list"
# response=$(object_list $id_token $access_token)
# echo "${response}" | jq
# file=$(echo "${response}" | jq .[0].object_name | awk -F'"' '{print $2}')
#
#
# echo "### TEST: Download file ${file}"
# response=$(download_file $file)
# echo "${response}"
#
#
# echo "### TEST: Upload file ${file}"
# response=$(upload_file $file)
# echo "${response}" | jq

# echo "### TEST: Create organization named OrganizationTest"
# response=$(create_organization $access_token)
# echo "${response}" | jq
#
#
# i=0
# resp=$(echo "${response}" | jq .status | awk -F'"' '{print $2}')
# while [[ "${resp}" != "CREATE_COMPLETE" && $i -le 20 ]]; do
#   #statements
#   echo "### TEST [${i}]: Get organization named OrganizationTest"
#   response=$(get_organization $access_token)
#   echo "${response}" | jq
#   resp=$(echo "${response}" | jq .status | awk -F'"' '{print $2}')
#   sleep 1
#   i=$(( $i + 1 ))
# done


echo "### TEST: Delete organization named OrganizationTest"
response=$(delete_organization $access_token)
echo "${response}" | jq


echo "### TEST: Refresh token"
response=$(refresh_token $refresh_token $access_token)
echo "${response}" | jq
access_token=$(echo ${response} | jq .access_token | awk -F'"' '{print $2}')
id_token=$(echo ${response} | jq .id_token | awk -F'"' '{print $2}')
refresh_token=$(echo ${response} | jq .refresh_token | awk -F'"' '{print $2}')


echo "### TEST: Logout"
response=$(logout $refresh_token $access_token)
echo "${response}" | jq


echo "### TEST: User info"
response=$(user_info $access_token)
echo "${response}" | jq
