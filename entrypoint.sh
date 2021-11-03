#!/bin/bash
cd /oos-pkgs-checker
python3 check.py --openstack-release "${OPENSTACK_RELEASE}" --openeuler-release "${OPENEULER_RELEASE}" --gitee-pat "${GITEE_PAT}"

echo $?