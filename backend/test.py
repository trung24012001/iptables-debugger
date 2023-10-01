import os
import platform
from iptables_handler import IptablesHandler
from iptables_namespace import IptablesNS
from nsenter import Namespace

if platform.system() != "Linux":
    exit("Only supported on Linux.")

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.")

iptablesns = IptablesNS()


if __name__ == "__main__":
    packet = {
        "state": "NEW",
        "saddr": "1.2.3.4",
        "daddr": "2.3.4.5",
        "prot": "icmp",
        "sport": None,
        "dport": None,
        "smac": None,
        "dmac": None,
        "ininf": None,
        "outinf": None,
    }
    #filename = "ruleset-mmt67.iptables"
    #ns = iptablesns.setup(filename)
    #print(ns)
    ns = "f376b19b"
    with Namespace(f"/var/run/netns/{ns}", "net"):
        iptables = IptablesHandler()
        results = iptables.import_packet(packet)
        print(results)
