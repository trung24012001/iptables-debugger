#!/bin/bash

set -e

if [ "$(id -u -n)" != "root" ]; then
    echo "need to be root, please run with sudo" >&2
    exit 1
fi

if [ -z "$(which curl)" ]; then
    echo "curl not found" >&2
    exit 1
fi

if [ -z "$(which ipset)" ]; then
    echo "ipset not found" >&2
    exit 1
fi

send () {
    curl -X POST \
        -F "ipset=<-" \
        "{{ url }}/{{ netns }}/ipset"
}

ipset save | send >/dev/null 2>&1
