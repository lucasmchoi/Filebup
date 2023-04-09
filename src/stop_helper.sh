#!/bin/bash
# stop all docker containers
for id in $dockerids; do
    [[ $id = $ownshortid* ]] || curl -s -XPOST --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http:/containers/$id/stop
done

# wait until all docker cointainers stopped
while true; do
    currentnum=$(curl --silent -XGET --unix-socket /var/run/docker.sock http://localhost/containers/json | jq -r '.[].Id' | wc -l)
    if [ $currentnum -ne $dockernum ]; then
        break
    fi
    sleep 1
done
