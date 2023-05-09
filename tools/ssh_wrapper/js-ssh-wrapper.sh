#!/bin/bash
################################################################################
# Copyright (c) 2017-2021 UCit SAS
# All Rights Reserved
#
# This software is the confidential and proprietary information
# of UCit SAS ("Confidential Information").
# You shall not disclose such Confidential Information
# and shall use it only in accordance with the terms of
# the license agreement you entered into with UCit.
################################################################################

# Variables such as CLUSTER_REMOTE_HOST, SSH_USER, SSH_KEY defines how you want to submit jobs on the remote cluster
# For example: SSH_USER=${USER} and SSH_KEY="/home/${SSH_USER}/.ssh/id_rsa" will allow the user to connect to the cluster with their own key
# This case will force the user to have his own SSH key

# UPDATEME:
# Declare where is the remotized cluster
CLUSTER_REMOTE_HOST=192.168.20.118

# UPDATEME:
# Declare the SSH user
SSH_USER=${USER}

# UPDATEME:
# Declare SSH Key location
SSH_KEY="/home/${SSH_USER}/.ssh/id_rsa"

# UPDATEME:
# Enable logs: 0:nothing | 1: log all commands
DEBUG=0


###############################################################################
# Declare log structure and folder
SCRIPTDIR="$(dirname "${BASH_SOURCE[0]}")"
WRAPPER_LOG_DIR="/${SCRIPTDIR}/log/"
TODAY=$(date +"%y-%b-%d")

LANG=C

# Declare commands which are using stdin inputs
CMD_WITH_STDIN_INPUTS=(
   # SLURM
   sbatch

   # LSF
   bsub
)

# We need to parse the input arguments and handle them correclty, especially those
# enclosed in double-quotes. If we simply pass "$@" to the command executed through
# ssh, a double-quoted argument that contains spaces will be considered as multiple
# arguments
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

declare -a args
count=0
for arg in "$@"; do
    args[count]=$(printf '%q' "$arg")
    count=$((count+1))
done

# Log
if [ ${DEBUG} == 1 ]; then
    if [ -z "${stdin}" ]; then stdin=""; fi
    if [ -z "${stdinput}" ]; then stdinput=""; fi
    echo "[${SSH_USER}]: ${SCRIPT_NAME} " "${args[@]}" " < ${stdin} ${stdinput}" >> "${WRAPPER_LOG_DIR}/${TODAY}.log"
fi

# Here comes the tricky part (presented here for slurm, but it is similar for other
# job schedulers).
# 1. EnginFrame uses stdin to pass on the script to be submitted to sbatch
# 2. stdin is passed on from rgrid/bin/grid.submit, to slurm/grid/grid.submit, and
#    finally to slurm/bin/sbatch that calls in the end this script
# 3. The problem comes from slurm/bin/sbatch that sources slurm/bin/common, which
#    calls "scontrol show config" -> this calls this script, and stdin is then
#    "consumed" by the remote call to scontrol, leaving no stdin (and thus the job
#    script) to the subsequent call to sbatch
# 4. So we need to redirect stdin to /dev/null when the final command is not sbatch
#    This is done through the addition of the -n option to ssh
# 5. Last but not least: ssh does not transmit the environment variables to the remote
#    command. As EF passes services' parameters through environment variables, we must
#    transmit them, without disturbing the remote environment. Thus we need to exclude
#    some of the environment variables that are transmitted and which could cause problems
#    on the remote cluster (e.g., PATH, path to job scheduler binaries...)
declare -a envvars
excludevars=(PATH LD_LIBRARY_PATH PWD OLDPWD LSF_VERSION LSF_TOP EGO_TOP LSF_BINDIR LSF_SERVERDIR LSF_LIBDIR LSF_ENVDIR)
count=0
for v in $(compgen -e);do
    if [[ ! "${excludevars[*]}" =~ ${v} ]]; then
        envvars[count]="$v=\"${!v}\""
        count=$((count+1))
    fi
done

cmd=$(basename "$0")
if [[ ! " ${CMD_WITH_STDIN_INPUTS[*]} " =~ ${SCRIPT_NAME} ]]; then
    ssh -n -i "${SSH_KEY}" "${SSH_USER}@${CLUSTER_REMOTE_HOST}" "${envvars[@]}" "${cmd}" "${args[@]}"
else
    # Some commands receive some inputs through stdin
    # in this case, the -n option of ssh mustn't be specified
    ssh -i "${SSH_KEY}" "${SSH_USER}@${CLUSTER_REMOTE_HOST}" "${envvars[@]}" "${cmd}" "${args[@]}"
fi

exit $?
