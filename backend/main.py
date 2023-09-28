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
        "src": "1.2.3.4",
        "dst": "2.3.4.5",
        "prot": "icmp",
        "sport": None,
        "dport": None,
        "smac": None,
        "dmac": None,
        "state": "NEW",
        "inif": None,
        "outif": None,
    }
    #filename = "ruleset-mmt67.iptables"
    #ns = iptablesns.setup(filename)
    ns = "f376b19b"
    #print(ns)
    with Namespace(f"/var/run/netns/{ns}", "net"):
        iptables = IptablesHandler()
        iptables.import_packet(packet)
        print(iptables.chains)
        results = iptables.import_packet(packet)
        print(results)
