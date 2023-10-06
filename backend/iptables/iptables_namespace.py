import os
import uuid
import subprocess
import pathlib
from netifaces import interfaces, ifaddresses, AF_INET, AF_LINK
from nsenter import Namespace


class IptablesNS:
    def __init__(self):
        pass

    def addns(self, ns):
        subprocess.check_call(["ip", "netns", "add", ns])
        return ns

    def delns(self, ns):
        subprocess.check_call(["ip", "netns", "delete", ns])
        return True
    
    def findns(self, ns):
        return ns in os.listdir("/var/run/netns/")

    def init_iptables(self, filepath, ns):
        subprocess.check_call(f"ip netns exec {ns} iptables-restore < {filepath}", shell=True)
        subprocess.check_call(f"ip netns exec {ns} ip link add br0 type bridge", shell=True)
        return True

    def get_iptables(self, ns):
        output = subprocess.check_output(f"ip netns exec {ns} iptables-save", shell=True)
        return output

    def init_interfaces(self, infs, ns):
        for inf in infs:
            subprocess.check_call(f"ip netns exec {ns} ip link add {inf['name']} address {inf['mac']} type dummy", shell=True)
            if inf["addr"]:
                subprocess.check_call(f"ip netns exec {ns} ip addr add {inf['addr']} dev {inf['name']}", shell=True)
            if inf["type"] == "bridge_slave":
                subprocess.check_call(f"ip netns exec {ns} ip link set dev {inf['name']} master br0", shell=True)

        return True

    def get_interfaces(self, ns):
        with Namespace(f"/var/run/netns/{ns}", "net"):
            ifaces = []
            for ifname in interfaces():
                ifaddrs = ifaddresses(ifname)
                addr = None
                mac = None
                if ifaddrs.get(AF_INET):
                    addr = ifaddresses(ifname)[AF_INET][0]["addr"]
                if ifaddrs.get(AF_LINK):
                    mac = ifaddresses(ifname)[AF_LINK][0]["addr"]
                ifaces.append({"ifname": ifname, "addr": addr, "mac": mac})
            return ifaces

