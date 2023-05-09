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


# Base image
FROM rockylinux/rockylinux:8

# Install ansible and prerequisites
RUN yum update -y \
&& yum install epel-release -y
RUN yum install jq ansible redhat-lsb -y
RUN ansible-galaxy collection install ansible.posix community.general

# Copy the deployment directory and execute post-install script
VOLUME /opt/heroes/platform/sbin
WORKDIR /opt/heroes/platform/sbin
COPY . .
RUN ./scripts/post-install.sh

# Start fastapi server with start.sh script and args provided
# at container launch
ENTRYPOINT ["/opt/heroes/platform/sbin/scripts/start.sh"]
