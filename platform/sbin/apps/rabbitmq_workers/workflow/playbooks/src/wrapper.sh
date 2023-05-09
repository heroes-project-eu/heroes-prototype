#!/bin/bash


# Generic variables
workflowsDir="/efs/work"
fastapiUrl="fastapi.heroes.doit.priv"
registryUrl=""

get_credentials() {
  ###
  # HEROES - Get credentials
  #
  # This function allows to get the next variables from the HEROES database:
  #   - user:     The user of the cluster.
  #   - address:  The address of the cluster.
  #   - sshKey:   The sshKey associated to the user of the cluster.
  ###
  clusterName=$1
  # set -x
  # # Todo: FastAPI url to the correct function when it will be implemented.
  # # Todo: A way to get token
  # response=$(curl --insecure -s -X 'GET' \
  # "https://${fastapiUrl}/organization/.../${clusterName}/list/" \
  # -H 'accept: application/json' \
  # -H "token: ${token}")
  # set +x

  ### Tmp
  credentials_cluster1=("centos" "ec2-63-34-85-93.eu-west-1.compute.amazonaws.com" "/opt/rabbitmq/keys/heroes_tech.pem")
  credentials_cluster2=("centos" "ec2-54-220-255-126.eu-west-1.compute.amazonaws.com" "/opt/rabbitmq/keys/heroes_tech.pem")

  if [[ "${clusterName}" == "cluster1" ]]; then
    echo "${credentials_cluster1[@]}"
  elif [[ "${clusterName}" == "cluster2" ]]; then
    echo "${credentials_cluster2[@]}"
  fi
  ### End of tmp

  # echo "${response}"
}


copy_files() {
  ###
  # HEROES - Copy files
  #
  # This function allows to copy the Nextflow run scripts to the correct
  # cluster. It needs the next arguments:
  #   - workDir:      The Nextflow work directory.
  #   - file:         The Nextflow run script files.
  #   - clusterName:  The cluster where the files should be copied.
  ###
  workDir=$1
  clusterName=$2
  singularityImage=$3
  wfDir=$(echo "${workDir}" | awk -F'/' '{print $1"/"$2"/"$3}')
  i=0

  for v in $(get_credentials ${clusterName}); do
    credentials[i]="${v}"
    ((i=i+1))
  done

  echo "### SINGULARITY ###" >> /tmp/wrapper.log
  echo "${workflowsDir}/${workDir}/" >> /tmp/wrapper.log
  echo "${workflowsDir}/${wfDir}" >> /tmp/wrapper.log
  echo "${singularityImage}" >> /tmp/wrapper.log
  echo "### SINGULARITY ###" >> /tmp/wrapper.log

  singularityImageName=$(basename $singularityImage)
  cpResult=$(cp "/opt/rabbitmq/images/${singularityImageName}" "${workflowsDir}/${wfDir}")
  # singularity -q pull --dir "${workflowsDir}/${workDir}/" "${singularityImageName}" 2>&1 >/dev/null

  echo "### RSYNC ###" >> /tmp/wrapper.log
  echo "${credentials[2]}" >> /tmp/wrapper.log
  echo "${workflowsDir}/${wfDir}/" >> /tmp/wrapper.log
  echo "${credentials[0]}@${credentials[1]}:${workflowsDir}/${wfDir}/" >> /tmp/wrapper.log
  echo "### RSYNC ###" >> /tmp/wrapper.log

  sshResult=$(ssh -i "${credentials[2]}" "${credentials[0]}@${credentials[1]}" "mkdir -p ${workflowsDir}/${wfDir}/")
  rsyncResult=$(rsync -avz -e "ssh -i ${credentials[2]}" "${workflowsDir}/${wfDir}/" "${credentials[0]}@${credentials[1]}:${workflowsDir}/${wfDir}/" 2>&1 >/dev/null)
}


copy_files_to_local() {
  ###
  # HEROES - Copy files
  #
  # This function allows to copy the Nextflow run scripts to the correct
  # cluster. It needs the next arguments:
  #   - workDir:      The Nextflow work directory.
  #   - file:         The Nextflow run script files.
  #   - clusterName:  The cluster where the files should be copied.
  ###
  workDir=$1
  #file=$2
  clusterName=$2
  i=0
  for v in $(get_credentials ${clusterName}); do
    credentials[i]="${v}"
    ((i=i+1))
  done

  scp -rpq -i "${credentials[2]}" "${credentials[0]}@${credentials[1]}:${workflowsDir}/${workDir}/*" "${workflowsDir}/${workDir}"
  scp -pq -i "${credentials[2]}" "${credentials[0]}@${credentials[1]}:${workflowsDir}/${workDir}/.*" "${workflowsDir}/${workDir}"

  echo scp -pq -i "${credentials[2]}" "${credentials[0]}@${credentials[1]}:${workflowsDir}/${workDir}/*" "${workflowsDir}/${workDir}"
  echo scp -pq -i "${credentials[2]}" "${credentials[0]}@${credentials[1]}:${workflowsDir}/${workDir}/.*" "${workflowsDir}/${workDir}"
}


ssh_endpoint() {
  ###
  # HEROES - ssh url
  #
  # This function returns the ssh endpoint to Nextflow.
  # It needs the following arguments:
  #   - workDir:      The Nextflow work directory.
  #   - file:         The Nextflow run script files needed for job execution.
  #   - clusterName:  The cluster selected for the job execution.
  ###
  workDir=$1
  clusterName=$2
  file='.command.run'

  i=0
  for v in $(get_credentials ${clusterName}); do
    credentials[i]="${v}"
    ((i=i+1))
  done

  echo "${credentials[2]}" "${credentials[0]}@${credentials[1]}" "${workflowsDir}/${workDir}/${file}"
}


main() {
  # Arguments
  action=$1
  workDir=$2
  workDir=$(echo "${workDir}" | awk -F'/work/' '{print $2}')
  clusterConfig=$3
  imagePath=$4

  echo $@ >> /tmp/wrapper.log

  clusterConfig=$(echo "${clusterConfig}" | sed "s/\[//" | sed "s/\]//" | sed "s/'//" | sed "s/'//")
  echo "${clusterConfig}" >> /tmp/wrapper.log

  IFS=',' read -r -a clusterConfigList <<< "$clusterConfig"
  echo "### BEGIN OF LOOP ###" >> /tmp/wrapper.log
  for clusterOption in "${clusterConfigList[@]}"; do
    clusterOptionKey=$(echo "${clusterOption}" | awk -F'=' '{print $1}')
    clusterOptionValue=$(echo "${clusterOption}" | awk -F'=' '{print $2}')

    if [[ "${clusterOptionKey}" == "name" ]]; then
      clusterName="${clusterOptionValue}"
    elif [[ "${clusterOptionKey}" == "user" ]]; then
      clusterUser="${clusterOptionValue}"
    elif [[ "${clusterOptionKey}" == "address" ]]; then
      clusterAddress="${clusterOptionValue}"
    elif [[ "${clusterOptionKey}" == "ssh_path" ]]; then
      clusterSshPath="${clusterOptionValue}"
    fi
    echo "${clusterOptionKey} = ${clusterOptionValue}" >> /tmp/wrapper.log
  done
  echo "### END OF LOOP ###" >> /tmp/wrapper.log

  #clusterName="cluster1"

  # Add the to the know hosts
  clusterIpV4=$(host "${clusterAddress}" | awk -F' ' '{print $4}')
  addKnowHost=$(ssh-keyscan -t rsa "${clusterAddress},${clusterIpV4}" >> ~/.ssh/known_hosts 2> /dev/null)

  if [[ "${action}" == "submit" ]]; then
    copy_files "${workDir}" "${clusterName}" "${imagePath}"
    ssh_endpoint "${workDir}" "${clusterName}"
  elif [[ "${action}" == "status" ]]; then
    copy_files_to_local "${workDir}" "${clusterName}"
  fi
}


main "$@"
