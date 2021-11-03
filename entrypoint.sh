#!/bin/bash
cd /oos-pkgs-checker
python3 check.py --openstack-release "${INPUT_OPENSTACK_RELEASE}" \
--openeuler-release "${INPUT_OPENEULER_RELEASE}" \
--gitee-pat "${INPUT_GITEE_PAT}"

echo $?