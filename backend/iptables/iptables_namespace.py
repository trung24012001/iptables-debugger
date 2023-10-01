import os
import uuid
import subprocess
import pathlib

class IptablesNS:
    def __init__(self):
        self.filedir = pathlib.Path(__file__).parent.resolve() / "ruleset"

    def addns(self, ns):
        subprocess.check_call(["ip", "netns", "add", ns])
        return ns

    def delns(self, ns):
        subprocess.check_call(["ip", "netns", "delete", ns])
        return True
    
    def findns(self, ns):
        return ns in os.listdir("/var/run/netns/")

    def init_iptables(self, filename, ns):
        subprocess.check_call(f"ip netns exec {ns} iptables-restore < {self.filedir}/{filename}", shell=True)
        return True

    def get_iptables(self, ns):
        output = subprocess.check_output(f"ip netns exec {ns} iptables-save", shell=True)
        return output
