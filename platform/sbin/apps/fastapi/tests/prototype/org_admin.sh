#!/bin/bash


# Vars
fastapi_url="api.heroes-project.eu"
bucket_name="xxxx"
organization="xxxx"
username="xxxx"
password="xxxx"


new_user_name="xxxx"
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


function create_subfolder() {
  token=$1
  bucket=$2
  subfolder_path=$3
  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/data/bucket/${bucket}/?subfolder_path=${subfolder_path}" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json'
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


function create_cluster() {
  token=$1
  name=$2
  user=$3
  endpoint=$4
  ssh_key=$5
  work_dir=$6
  port=$7

  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/admin/cluster/" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json' \
  -d "{\"name\": \"${name}\", \"user\": \"${user}\", \"endpoint\": \"${endpoint}\", \"ssh_key\": \"${ssh_key}\", \"port\": \"${port}\", \"work_dir\": \"${work_dir}\"}"
  set +x
}


function create_workflow() {
  token=$1
  name=$2
  description=$3
  script_template_path=$4
  container_path=$5
  application=$6
  set -x
  curl --insecure -s -X 'POST' \
  "https://${fastapi_url}/organization/admin/workflow/template" \
  -H 'accept: application/json' \
  -H "token: ${token}" \
  -H 'Content-Type: application/json' \
  -d "{\"name\": \"${name}\", \"description\": \"${description}\", \"script_template_path\": \"${script_template_path}\", \"container_path\": \"${container_path}\", \"application\": \"${application}\"}"
  set +x
}


clear
echo "### TEST: Login"
response=$(login)
token=$response
echo "${response}" | jq
read $wait_demo


# clear
# echo "### TEST: User info"
# response=$(user_info "${token}")
# echo "${response}" | jq
# read $wait_demo
#
#
# clear
# echo "### TEST: List users"
# response=$(list_users "${token}")
# echo "${response}" | jq
# read $wait_demo

#
# clear
# echo "### TEST: Create user named demouser"
# response=$(create_users "${token}" "demouser" "UCit2022!!")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="basicuser"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="jorik"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="benjamin"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="anaelle"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="sablin"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="philippe"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="benoit"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="vincent"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="ugur"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="nicolas"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
# clear
# echo "### TEST: Get user info"
#   response=$(get_user "${token}" "${new_user_name}")
# echo "${response}" | jq
# read $wait_demo
#
# new_user_name="demouser"
# echo "### TEST: Create user named ${new_user_name}"
# response=$(create_users "${token}" "${new_user_name}" "${new_user_password}")
# echo "${response}" | jq
# read $wait_demo
#
#
# clear
# echo "### TEST: Get user info"
#   response=$(get_user "${token}" "${new_user_name}")
# echo "${response}" | jq
# read $wait_demo
# clear
# echo "### TEST: Delete user named ${new_user_name}"
# response=$(delete_user "${token}" "${new_user_name}")
# echo "${response}" | jq
# read $wait_demo
#
#
# clear
# echo "### TEST: Get user info"
#   response=$(get_user "${token}" "${new_user_name}")
# echo "${response}" | jq
# read $wait_demo


# clear
# echo "### TEST: List groups"
# response=$(list_groups "${token}")
# echo "${response}" | jq
# read $wait_demo
#
#
# clear
# echo "### TEST: Create group named demogroup"
# response=$(create_groups "${token}" "demogroup")
# echo "${response}" | jq
# read $wait_demo
#
#
# clear
# echo "### TEST: Get group info"
# response=$(get_group "${token}" "demogroup")
# echo "${response}" | jq
# read $wait_demo
#
#
# clear
# echo "### TEST: Delete groupe named testGrp"
# response=$(delete_group "${token}" "demogroup")
# echo "${response}" | jq
# read $wait_demo


clear
echo "### TEST: Data list"
response=$(data_list "${token}")
echo "${response}" | jq
read $wait_demo


# clear
# echo "### TEST: Create cluster main_cluster"
# response=$(create_cluster "${token}" "main_cluster" "hsuser" "ec2-54-220-255-126.eu-west-1.compute.amazonaws.com" "/opt/rabbitmq/keys/heroes_tech.pem" "/efs/work" "22")
# echo "${response}" | jq
# read $wait_demo
#
# clear
# echo "### TEST: Create cluster second_cluster"
# response=$(create_cluster "${token}" "second_cluster" "hsuser" "gateway.hpcnow.com" "/opt/rabbitmq/keys/heroes_tech.pem" "/cm/work" "60122")
# echo "${response}" | jq
# read $wait_demo
#
# clear
# echo "### TEST: Create cluster third_cluster"
# response=$(create_cluster "${token}" "third_cluster" "hsuser" "ec2-63-34-85-93.eu-west-1.compute.amazonaws.com" "/opt/rabbitmq/keys/heroes_tech.pem" "/efs/work" "22")
# echo "${response}" | jq
# read $wait_demo

# clear
# echo "### TEST: Create cluster test_cluster"
# response=$(create_cluster "${token}" "test_cluster" "hsuser" "ec2-54-220-255-126.eu-west-1.compute.amazonaws.com" "/opt/rabbitmq/keys/heroes_tech.pem" "/efs/work" "22")
# echo "${response}" | jq
# read $wait_demo

clear
echo "### TEST: Create subfolder wf1-input"
response=$(create_subfolder "${token}" "basicuser" "wf1-input")
echo "${response}" | jq
read $wait_demo

clear
echo "### TEST: Create subfolder wf2-input"
response=$(create_subfolder "${token}" "basicuser" "wf2-input")
echo "${response}" | jq
read $wait_demo

clear
echo "### TEST: Create subfolder wf3-input"
response=$(create_subfolder "${token}" "basicuser" "wf3-input")
echo "${response}" | jq
read $wait_demo


### Create workflows ###
clear
echo "### TEST: Create subfolder dummy-workflow"
response=$(create_subfolder "${token}" "basicuser" "dummy-workflow")
echo "${response}" | jq
read $wait_demo


clear
echo "### TEST: Create workflow dummy"
response=$(create_workflow "${token}" "dummy" "Dummy workflow" "/basicuser/dummy-workflow/main.nf" "/basicuser/dummy-workflow/alpine.3.8.simg" "openfoam")
echo "${response}" | jq
read $wait_demo

# clear
# echo "### TEST: Create subfolder openfoam-workflow"
# response=$(create_subfolder "${token}" "basicuser" "openfoam-workflow")
# echo "${response}" | jq
# read $wait_demo

clear
echo "### TEST: Create workflow openfoam"
response=$(create_workflow "${token}" "openfoam" "Openfoam workflow" "/basicuser/openfoam-workflow/main.nf" "/basicuser/openfoam-workflow/openfoam.sif" "openfoam")
echo "${response}" | jq
read $wait_demo

# clear
# echo "### TEST: Create subfolder tensorflow-workflow"
# response=$(create_subfolder "${token}" "basicuser" "tensorflow-workflow")
# echo "${response}" | jq
# read $wait_demo

echo "### TEST: Create workflow tensorflow"
response=$(create_workflow "${token}" "tensorflow" "Tensorflow workflow" "/basicuser/tensorflow-workflow/main.nf"  "/basicuser/tensorflow-workflow/tensorflow.sif" "tensorflow")
echo "${response}" | jq
read $wait_demo
