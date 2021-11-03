#!/bin/bash
python3 check.py --openstack-release "${OPENSTACK_RELEASE}" --openeuler-release "${OPENEULER_RELEASE}"

echo $?