#!/bin/bash

set -e

send () {
    curl -X POST \
        -F "interfaces=<-" \
        "{{ url }}/{{ netns }}/interfaces"
}

result="["

interfaces=$(ip -o link show | grep 'ether' | awk -F': ' '{print $2}' | awk -F '@' '{print $1}')

first=true
for interface in $interfaces; do
    if [ $interface == "lo" ]; then
        continue
    fi

    state=$(ip -o link show dev $interface | awk -F 'state' '{print $2}' | awk '{print $1}')

    if [ $state == "DOWN" ]; then
        continue
    fi

    ip_address=$(ip -o addr show dev $interface | awk '/inet / {print $4}')

    mac_address=$(ip link show dev $interface | awk 'NR==2' | awk '{print $2}')

    iface_type=$(ip -d link show dev $interface | awk 'NR==3' | awk '{print $1}')

    bridge=$(ip -d link show dev $interface | awk 'NR==4' | awk '{print $1}')
    
    master=$(ip -o link show dev $interface | awk -F 'master' '{print $2}' | awk '{print $1}')
      
    if [[ $iface_type =~ ^bridge_slave* ]]; then
        bridge=$iface_type
    fi

    row="{\"ifname\": \"$interface\", \"state\": \"$state\", \"bridge\": \"$bridge\", \"master\": \"$master\",  \"type\": \"$iface_type\", \"ip\": \"$ip_address\", \"mac\": \"$mac_address\"}"
    if [ "$first" = true ]; then
        result+=$row
        first=false
    else
        result+=", $row"
    fi
done

result+="]"

echo $result | send >/dev/null 2>&1

