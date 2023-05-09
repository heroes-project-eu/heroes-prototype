#!/bin/bash


# Vars
fastapi_url="api.heroes-project.eu"
organization="master"
username="xxxx"
password="xxxx"

new_user_name="basicuser"
new_user_password="xxxx"
new_user_organization="xxxx"
email="basicuser@mockuporg.eu"


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


function refresh_token() {
  token=$1
  set -x
  curl --insecure -s 'GET' \
  "https://${fastapi_url}/organization/auth/refresh_token?organization=${organization}" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


function logout() {
  token=$1
  set -x
  curl --insecure -s 'POST' \
  "https://${fastapi_url}/organization/auth/logout?organization=${organization}" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


function create_organization() {
  token=$1
  set -x
  curl --insecure -s 'POST' \
  "https://${fastapi_url}/heroes/admin/organizations/?user_email=${email}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json' \
  -d "{\"name\": \"${new_user_organization}\"}"
  set +x
}


function get_organization() {
  token=$1
  organization_target=$2
  set -x
  curl --insecure -s 'GET' \
  "https://${fastapi_url}/heroes/admin/organizations/${organization_target}" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


function create_users() {
  token=$1
  user_name=$2
  user_organization=$3
  user_password=$4
  user_email="${user_name}@${user_organization}.fr"
  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/admin/users/?user_name=${user_name}&user_email=${user_email}&user_password=${user_password}&organization=${user_organization}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
  set +x
}


function delete_organization() {
  token=$1
  organization_target=$2
  response=$(curl --insecure -s -X 'DELETE' \
  "https://${fastapi_url}/heroes/admin/organizations/?organization_target=${organization_target}" \
  -H 'accept: application/json' \
  -H "token: ${token}")
  echo "${response}"
}


clear
echo "### TEST: Login"
response=$(login)
token="${response}"
echo "${response}" | jq
read $wait_demo


# clear
# echo "### TEST: User info"
# response=$(user_info "${token}")
# echo "${response}" | jq
# read $wait_demo
#
#
clear
echo "### TEST: Create organization named ${new_user_organization}"
response=$(create_organization "${token}")
echo "${response}" | jq
read $wait_demo


# i=0
# resp=$(echo "${response}" .status | awk -F'"' '{print $2}')
# while [[ "${resp}" != "CREATE_COMPLETE" && $i -le 20 ]]; do
#   clear
#   echo "### TEST [${i}]: Get organization named ${new_user_organization}"
#   response=$(get_organization "${token}" "${new_user_organization}")
#   if [[ (($i -gt 2 )) ]]; then
#     response=$(echo "${response}" | sed -e "s/CREATE_IN_PROGRESS/CREATE_COMPLETE/")
#   fi
#   echo "${response}"
#   resp=$(echo "${response}" | jq .status | awk -F'"' '{print $2}')
#   echo "${resp}"
#   sleep 1
#   i=$(( $i + 1 ))
# done
# read $wait_demo
#
#
#
# clear
# echo "### TEST: Delete organization named ${new_user_organization}"
# response=$(delete_organization "${token}" "${new_user_organization}")
# echo "${response}" | jq
# read $wait_demo


# clear
# echo "### TEST: Refresh token"
# response=$(refresh_token $refresh_token $access_token)
# echo "${response}"
# access_token=$(echo ${response} .access_token | awk -F'"' '{print $2}')
# id_token=$(echo ${response} .id_token | awk -F'"' '{print $2}')
# refresh_token=$(echo ${response} .refresh_token | awk -F'"' '{print $2}')
# read $wait_demo

#
# clear
# echo "### TEST: Logout"
# response=$(logout $refresh_token $access_token)
# echo "${response}"
# read $wait_demo


# clear
# echo "### TEST: User info"
# response=$(user_info $access_token)
# echo "${response}"
# read $wait_demo
