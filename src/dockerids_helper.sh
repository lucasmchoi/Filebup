#!/bin/bash
# get all docker container ids and number
dockerids=$(curl -s -XGET --unix-socket /var/run/docker.sock http://localhost/containers/json | jq -r '.[].Id')
dockernum=$(echo "$dockerids" | wc -l)
ownshortid=$HOSTNAME