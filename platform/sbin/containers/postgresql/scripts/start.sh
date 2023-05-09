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


# DataBase Initialization
cp -r /opt/heroes/platform/sbin/conf/pgsql/ /var/lib/
chown -R postgresql:postgresql /var/lib/pgsql

# Start postgresql
runuser -l postgresql -c '/usr/bin/postmaster -D /var/lib/pgsql/data' &
postgresql_pid=$!
sleep 5

# Create superuser named 'heroes'
password='xxxx'
expect - <<EOF
spawn runuser -l postgresql -c "createuser -P -s -e heroes"
expect "Enter password for new role:"
send "$password\n"
expect "Enter it again:"
send "$password\n"
interact
EOF

# Create a database named 'heroes'
runuser -l postgresql -c 'createdb -O heroes heroes'

# Wait for any process to exit
wait $postgresql_pid
exit_pid=$?

# Exit with status of process that exited first
exit $exit_pid
