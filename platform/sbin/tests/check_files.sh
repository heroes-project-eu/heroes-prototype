#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
backpwd="${PWD}"

rv=0

cd_prev_dir() {
  cd "${backpwd}" || return
}

trap cd_prev_dir SIGINT SIGTERM SIGUSR1 SIGUSR2

cd "${DIR}" || exit 1

# Run shellcheck on all .sh files in scripts
echo "# Checking .sh scripts with shellcheck"
find "${DIR}/../scripts" -iname '*.sh' -print0 | xargs -0 shellcheck
scrv=$?
if [ ${scrv} -ne 0 ]; then
  rv=$((rv+1))
fi
echo ""

shopt -s globstar nullglob


# Run ansible-playbook to validate yaml files in playbooks
echo "# Checking .yaml scripts with ansible-playbook"

# Remove warnings
export ANSIBLE_LOCALHOST_WARNING=False

# Create a temporary inventory file
invfile=$(mktemp)
cat > "${invfile}" <<EOF
[localhost]
127.0.0.1  ansible_connection=local
EOF

for f in "${DIR}"/../playbooks/*.yaml; do
  grep "# SKIP ANSIBLE CHECK SYNTAX - NOT A PLAYBOOK" "$f" >/dev/null 2>&1
  rv=$?
  if [ ${rv} == 0 ];then
    echo "# Skipping $f - not an ansible playbook"
    continue
  fi

  echo "# Checking $f with ansible-playbook"
  ansible-playbook -i "${invfile}" --syntax-check "$f"
  anspbrv=$?
  if [ ${anspbrv} -ne 0 ]; then
    rv=$((rv+1))
  fi
done

rm -f "${invfile}"

exit ${rv}
