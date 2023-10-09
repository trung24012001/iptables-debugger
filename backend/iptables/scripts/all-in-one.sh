#!/bin/sh

set -e

if [ "$(id -u -n)" != "root" ]; then
    echo "need to be root, please run with sudo" >&2
    exit 1
fi

if [ -z "$(which iptables-save)" ]; then
    echo "iptables-save not found" >&2
    exit 1
fi

if [ -z "$(which curl)" ]; then
    echo "not sure how you downloaded me, but curl not found" >&2
    exit 1
fi

send () {
    curl -s -X POST \
        -F "rules=<-" \
        "{{ url }}/iptables"
}

netns=$(iptables-save | send)

if [ -n "$netns" ]; then
    curl -s "{{ url }}/$netns/interfaces" | bash 
    curl -s "{{ url }}/$netns/ipset" | bash 
fi

echo "{{ result_url }}/$netns"

