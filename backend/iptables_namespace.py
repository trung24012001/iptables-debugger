import os
import uuid
import subprocess


class IptablesNS:
    def __init__(self):
        pass

    def setup(self, filename):
        ns = str(uuid.uuid4())[:8]
        self.add_ns(ns)
        try:
            self.init_iptables(filename, ns)
        except:
            self.del_ns(ns)
            raise Exception("Fail to init iptables")

        return ns

    def add_ns(self, ns):
        subprocess.check_call(["ip", "netns", "add", ns])

    def del_ns(self, ns):
        subprocess.check_call(["ip", "netns", "delete", ns])
    
    def find_ns(self, ns):
        return ns in os.listdir("/var/run/netns/")

    def init_iptables(self, filename, ns):
        subprocess.check_call(f"ip netns exec {ns} iptables-restore < {os.path.dirname(os.path.abspath(__file__))}/{filename}", shell=True)
