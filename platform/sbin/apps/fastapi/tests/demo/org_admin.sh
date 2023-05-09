#!/bin/bash


# Vars
fastapi_url="fastapi.heroes.doit.priv"
organization="xxxx"
bucket_name="xxxx"
username="xxxx"
password="xxxx"


new_user_name="basicuser"
new_user_password="xxxx"
new_user_organization="mockuporg"
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


function data_list() {
  token=$1
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/data/list" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


function create_bucket() {
  token=$1
  bucket_name=$2
  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/data/bucket?bucket_name=${bucket_name}" \
  -H 'accept: application/json' \
  -H "token: ${token}"
  set +x
}


function delete_bucket() {
  token=$1
  bucket_name=$2
  set -x
  curl --insecure -s -X 'DELETE' \
  "https://${fastapi_url}/organization/databucket?bucket_name=${bucket_name}" \
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


function create_users() {
  token=$1
  user_name=$2
  user_email="${user_name}@ucit.fr"
  user_password=$3
  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/admin/users/?user_name=${user_name}&user_email=${user_email}&user_password=${user_password}&organization=${organization}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
  set +x
}


function list_users() {
  token=$1
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/admin/users/" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
  set +x
}


function get_user() {
  token=$1
  username=$2
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/admin/users/${username}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
  set +x
}


function delete_user() {
  token=$1
  username=$2
  set -x
  curl --insecure -s -X 'DELETE' \
  "https://${fastapi_url}/organization/admin/users/${username}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
  set +x
}


function list_groups() {
  token=$1
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/admin/groups/" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
  set +x
}


function create_groups() {
  token=$1
  groupname=$2
  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/admin/groups/?groupname=${groupname}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
  set +x
}


function get_group() {
  token=$1
  groupname=$2
  set -x
  curl --insecure -s -X 'GET' \
  "https://${fastapi_url}/organization/admin/groups/${groupname}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
  set +x
}


function delete_group() {
  token=$1
  groupname=$2
  set -x
  curl --insecure -s -X 'DELETE' \
  "https://${fastapi_url}/organization/admin/groups/${groupname}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
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


clear
echo "### TEST: List users"
response=$(list_users "${token}")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Create user named demouser"
response=$(create_users "${token}" "demouser" "UCit2022!!")
echo "${response}" | jq
read $wait_demo


echo "### TEST: Create user named ${new_user_name}"
response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
echo "${response}" | jq
read $wait_demo


echo "### TEST: Create multuple users"
for (( i = 2; i < 10; i++ )); do
  echo "### TEST: Create user named ${new_user_name}${i}"
  response=$(create_users "${token}" "${new_user_name}${i}" "${new_user_password}")
  echo "${response}" | jq
  read $wait_demo
done

clear
echo "### TEST: Get user info"
response=$(get_user "${token}" "demouser")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Delete user named demouser"
response=$(delete_user "${token}" "demouser")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: List groups"
response=$(list_groups "${token}")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Create group named demogroup"
response=$(create_groups "${token}" "demogroup")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Get group info"
response=$(get_group "${token}" "demogroup")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Delete groupe named testGrp"
response=$(delete_group "${token}" "demogroup")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Data list"
response=$(data_list "${token}")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Create bucket"
response=$(create_bucket "${token}" "demobucket")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Data list"
response=$(data_list "${token}")
echo "${response}" | jq
read $wait_demo
