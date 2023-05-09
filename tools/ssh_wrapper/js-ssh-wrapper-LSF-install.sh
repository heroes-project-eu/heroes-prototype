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

# Config parameters

## Declare LSF top directory
FAKE_LSF_TOP_DIR=$1

while [ -z "${FAKE_LSF_TOP_DIR}" ]
do
      echo "You must specify a directory for the installation of the SSH wrapper:"
      read -r FAKE_LSF_TOP_DIR
done

## List LSF commands
LSF_COMMANDS="augmentstarter bgbroker blaunch bqueues brsvdel bswitch egoexec lsclusters lsgrun lsmakerm lsunlockhost parallelupgrade.jar qjlist qwatch bacct bgdel blimits bread brsvjob btop egogenkey lseligible lshosts lsmon mpdstartup parallelupgrade.sh qlimit resmig badmin bgmod bmg breboot brsvmod bugroup egosh lsfhadoop.sh lsid lspasswd mpich2_wrapper pipeclient qmapmgr sca_mpimon_wrapper bapp bgpinfo bmgroup breconfig brsvs busers gmmpirun_wrapper lsfrestart lsinfo lsplace mpich_mx_wrapper pjllib.sh qmgr TaskStarter batch-acct bhist bmig brequeue brsvsub bwait init_energy lsfrsv lsload lsrcp mpichp4_wrapper pmd_w qps tspeek bbot bhosts bmod bresize brun ch initialize_eas lsfshutdown lsloadadj lsreconfig mpichsharemem_wrapper poejob qrestart tssub bchkpnt bhpart bmodify bresources bsla clnqs intelmpi_wrapper lsf-spark-shell.sh lslockhost lsreghost mpirun.lsf poe_w qrun user_post_exec_prog bclusters bjdepinfo bparams brestart bslots dnssec-keygen lammpirun_wrapper lsf-spark-submit.sh lslogin lsrtasks mvapich_wrapper ppmsetvar qsa user_pre_exec_prog bconf bjgroup bpeek bresume bstatus egoapplykey lsacct lsf-start-spark.sh lsltasks lsrun openmpi_rankfile.sh preservestarter qsnapshot xagent bentags bjobs bpost brlainfo bstop egoconfig lsacctmrg lsfstartup lsmake lsrun.sh openmpi_wrapper pvmjob qstat zapit bgadd bkill bqc brsvadd bsub egoenv lsadmin lsf-stop-spark.sh lsmake4 lstcsh pam qdel qsub"

# Create the LSF fake directory
mkdir -p "${FAKE_LSF_TOP_DIR}"

# Create LSF commands folder
mkdir -p "${FAKE_LSF_TOP_DIR}/bin"

# Create log folder
mkdir -p "${FAKE_LSF_TOP_DIR}/log"
chmod 757 "${FAKE_LSF_TOP_DIR}/log"

# Add symbolic links to the wrapper
for command in $LSF_COMMANDS
do
    ln -s "${FAKE_LSF_TOP_DIR}/js-ssh-wrapper.sh" "${FAKE_LSF_TOP_DIR}/bin/${command}"
done

# Create the default profile.lsf
cat << EOF > "${FAKE_LSF_TOP_DIR}/profile.lsf"
#!/bin/sh

LSF_VERSION=10.1
LSF_TOP="${FAKE_LSF_TOP_DIR}"
EGO_TOP="\${LSF_TOP}"
LSF_ENVDIR="\${LSF_TOP}"
LSF_BINDIR="\${LSF_TOP}/bin"

export LSF_VERSION LSF_TOP EGO_TOP LSF_ENVDIR LSF_BINDIR
export PATH="\$PATH:\$LSF_BINDIR"

EOF
