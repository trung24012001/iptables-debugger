import os
import platform
from iptables_handler import IptablesHandler

if platform.system() != "Linux":
    exit("Only supported on Linux.")

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.")

iptables = IptablesHandler()


if __name__ == "__main__":
    packet = {
        "src": "1.2.3.4",
        "dst": "2.3.4.5",
        "prot": "icmp",
        "sport": None,
        "dport": None,
        "in_inf": None,
        "out_inf": None,
        "state": "NEW",
    }
    filename = "ruleset-mmt67.iptables"
    ns = iptables.setup(filename)
    print(ns)
    rules = iptables.handle_packet(ns, packet)
    print(rules)
