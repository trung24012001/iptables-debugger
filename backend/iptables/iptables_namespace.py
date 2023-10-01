import os
import uuid
import subprocess
import pathlib

class IptablesNS:
    def __init__(self):
        self.filedir = pathlib.Path(__file__).parent.resolve() / "ruleset"

    def setup(self, filename, ns):
        self.addns(ns)
        try:
            self.init_iptables(filename, ns)
        except:
            self.delns(ns)
            raise Exception("Fail to init iptables")

        return ns

    def addns(self, ns):
        subprocess.check_call(["ip", "netns", "add", ns])

    def delns(self, ns):
        subprocess.check_call(["ip", "netns", "delete", ns])
    
    def findns(self, ns):
        return ns in os.listdir("/var/run/netns/")

    def init_iptables(self, filename, ns):
        subprocess.check_call(f"ip netns exec {ns} iptables-restore < {self.filedir}/{filename}", shell=True)
