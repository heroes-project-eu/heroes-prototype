#!/usr/bin/env bash

pushd $ansibleDir >/dev/null 2>&1
if [ \$? -eq "0" ]; then
	ansible-playbook $ansibleMain --tags $ansibleTags
else
        echo "Error entering the directory ${ansibleDir}, please check."
fi
popd >/dev/null 2>&1
