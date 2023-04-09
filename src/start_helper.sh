#!/bin/bash
# start all docker containers
for id in $dockerids; do
    [[ $id = $ownshortid* ]] || curl -s -XPOST --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' http:/containers/$id/start
done

# wait until all docker cointainers started
while true; do
    currentnum=$(curl --silent -XGET --unix-socket /var/run/docker.sock http://localhost/containers/json | jq -r '.[].Id' | wc -l)
    if [ $currentnum -eq $dockernum ]; then
        break
    fi
    sleep 1
done

unset dockerids dockernum ownshortid currentnum