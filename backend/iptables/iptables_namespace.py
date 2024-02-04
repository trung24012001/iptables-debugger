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
        subprocess.check_call(
            f"ip netns exec {ns} iptables-restore < {filepath}",
            shell=True,
        )
        return True

    def init_ipset(self, filepath, ns):
        subprocess.check_call(
            f"ip netns exec {ns} ipset restore < {filepath}", shell=True
        )
        return True

    def init_interfaces(self, interfaces, ns):
        for inf in interfaces:
            ifname = inf["ifname"]
            addr = inf["ip"]
            mac = inf["mac"]
            inf_type = "dummy"
            if inf["type"] == "bridge":
                inf_type = "bridge"
            bridge = inf["bridge"]
            master = inf["master"]

            try:
                command = f"ip netns exec {ns} ip link add {ifname} address {mac} type {inf_type}"
                subprocess.check_call(command, shell=True)
            except:
                continue

            if addr:
                command = f"ip netns exec {ns} ip addr add {addr} dev {ifname}"
                subprocess.check_call(command, shell=True)
            if bridge == "bridge_slave":
                command = f"ip netns exec {ns} ip link set dev {ifname} master {master}"
                subprocess.check_call(command, shell=True)

        return True

    def get_iptables(self, ns):
        output = subprocess.check_output(
            f"ip netns exec {ns} iptables-save", shell=True
        )
        return output

    def get_ipset(self, ns):
        output = subprocess.check_output(f"ip netns exec {ns} ipset save", shell=True)
        return output

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
