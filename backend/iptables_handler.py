import iptc
import ipaddress
import os
import uuid
import subprocess
from netifaces import ifaddresses, interfaces, AF_INET
from nsenter import Namespace


class IptablesHandler:
    def __init__(self):
        pass
        # self.ns = str(uuid.uuid4())[:8]

        # self.data_visualize = []
        # self.chains = []
        # self.tables = {}

        # self.addrInf = self.get_addrinf()

        # self.init_env()
        # self.init_iptables(filename)
        # self.init_chain()

    def setup(self, filename):
        ns = str(uuid.uuid4())[:8]
        self.add_ns(ns)
        self.init_iptables(ns)

        return ns

    # def init_chain(self):
    #     self.chains = ["PREROUTING", "ROUTING"]
    #     if self.addrInf.get(r["dst"]):
    #         self.chains = ["OUTPUT", "POSTROUTING"]
    #         r["out_inf"] = self.addrInf[r["src"]]
    #     elif self.addrInf.get(r["dst"]):
    #         r["in_inf"] = self.addrInf[r["dst"]]

    def add_ns(self, ns):
        subprocess.run(["ip", "netns", "add", ns], check=True)

    def del_ns(self, ns):
        subprocess.run(["ip", "netns", "delete", ns], check=True)

    def init_iptables(self, filename, ns):
        subprocess.run(
            ["ip", "netns", "exec", ns, "iptables-restore", "<", filename],
            check=True,
        )
        # with Namespace(f"/var/run/netns/{self.ns}", "net"):
        #     raws = iptc.easy.dump_table("raw")
        #     mangles = iptc.easy.dump_table("mangles")
        #     nats = iptc.easy.dump_table("nat")
        #     filters = iptc.easy.dump_table("filter")
        #     chains = ["PREROUTING", "INPUT", "FORWARD", "OUTPUT", "POSTROUTING"]
        #     for chain in chains:
        #         self.tables[chain] = []
        #         if raws.get(chain):
        #             self.tables[chain] += raws.get(chain)
        #         if mangles.get(chain):
        #             self.tables[chain] += mangles.get(chain)
        #         if nats.get(chain):
        #             self.tables[chain] += nats.get(chain)
        #         if filters.get(chain):
        #             self.tables[chain] += filters.get(chain)

    def handle_packet(self, packet):
        self.r = {
            "src": packet.src,
            "sport": packet.sport,
            "dst": packet.dst,
            "dport": packet.dport,
            "prot": packet.protocol,
            "in_inf": None,
            "out_inf": None,
            "state": packet.state,
        }

    def get_addrinf(self):
        addrInf = {}
        for ifaceName in interfaces():
            for i in ifaddresses(ifaceName).setdefault(AF_INET, [{"addr": None}]):
                addr = i["addr"]
                if addr:
                    addrInf[addr] = ifaceName
        return addrInf

    def get_bridges(inf):
        path = "/sys/class/net/{}/brif/".format(inf)
        return os.listdir(path)

    def set_chains(self):
        if self.addrInf.get(r["src"]):
            chains = ["OUTPUT", "POSTROUTING"]
        elif self.addrInf.get(r["dst"]):
            chains = ["INPUT"]
        else:
            chains = ["FORWARD", "POSTROUTING"]
        return chains

    def parse_addr(self, addr):
        if addr == None:
            addr = "0.0.0.0/0"
        elif addr.find("/") == -1:
            addr += "/32"
        if addr.find("!") != -1:
            addr = addr.split("!")[1]
            return list(
                ipaddress.ip_network("0.0.0.0/0").address_exclude(
                    ipaddress.ip_network(addr)
                )
            )
        return ipaddress.ip_network(addr)

    def parse_port(self, port):
        if port == None:
            port = "*"
        elif port.find(":") != -1:
            port = range(*list(map(lambda p: int(p), port.split(":"))))
        else:
            port = [int(port)]
        return port

    def parse_inf(self, inf):
        if inf == None:
            inf = "*"
        elif inf.find("!") != -1:
            tmp = inf.split("!")[1]
            inf = interfaces()
            inf.remove(tmp)
        else:
            inf = [inf]
        return inf

    def handle_address(self, rsrc, src):
        if rsrc == "*":
            return True
        rsrc = ipaddress.ip_address(rsrc)
        if isinstance(src, list):
            is_match = False
            for s in src:
                if rsrc in s:
                    is_match = True
            if not is_match:
                return False
        elif rsrc not in src:
            return False
        return True

    def handle_prot(self, rprot, rsport, rdport, prot, rule):
        if rprot == "*" or prot == None:
            return True
        if rprot != prot:
            return False
        port = rule.get(r["prot"])
        if port:
            sport = self.parse_port(port.get("sport"))
            dport = self.parse_port(port.get("dport"))
            if rsport != "*" and sport != "*":
                if int(rsport) not in sport:
                    return False
            if rdport != "*" and dport != "*":
                if int(rdport) not in dport:
                    return False
        return True

    def handle_inf(self, rinf, inf):
        if inf == "*":
            return True
        if rinf not in inf:
            return False
        return True

    def handle_physdev(self, rinf_in, rinf_out, physdev):
        if physdev == None:
            return True
        phys_in = physdev.get("physdev-in")
        phys_out = physdev.get("physdev-out")
        is_match = False
        if phys_in:
            if rinf_in == None:
                return False
            else:
                if phys_in in self.get_bridges(rinf_in):
                    is_match = True
                else:
                    is_match = False
        if phys_out:
            if rinf_out == None:
                return False
            else:
                if phys_out in self.get_bridges(rinf_out):
                    is_match = True
                else:
                    is_match = False
        return is_match

    def handle_mark(mark):
        # I will handle this later
        if mark == None:
            return True
        return False

    def handle_state(rstate, state):
        if rstate == "*" or state == None:
            return True
        states = (state.get("state") or state.get("ctstate")).split(",")
        if rstate not in states:
            return False
        return True

    def match_rule(self, rule, chain, num):
        src = self.parse_addr(rule.get("src"))
        dst = self.parse_addr(rule.get("dst"))
        inInf = self.parse_inf(rule.get("in-interface"))
        outInf = self.parse_inf(rule.get("out-interface"))
        prot = rule.get("protocol")
        target = rule.get("target")
        physdev = rule.get("physdev")
        mark = rule.get("mark")
        state = rule.get("state") or rule.get("conntrack")

        if not self.handle_address(r["src"], src):
            return False
        if not self.handle_address(r["dst"], dst):
            return False
        if not self.handle_prot(r["prot"], r["sport"], r["dport"], prot, rule):
            return False
        if not self.handle_inf(r["in_inf"], inInf):
            return False
        if not self.handle_inf(r["out_inf"], outInf):
            return False
        if not self.handle_physdev(r["in_inf"], r["out_inf"], physdev):
            return False
        if not self.handle_mark(mark):
            return False
        if not self.handle_state(r["state"], state):
            return False

        self.data_visualize.append(
            {"chain": chain, "rule": rule, "target": target, "num": num, "state": state}
        )

        return target

    def get_policy(chain):
        import subprocess

        if chain in ["PREROUTING", "POSTROUTING"]:
            return "ACCEPT"
        elif chain in ["INPUT", "FORWARD", "OUTPUT"]:
            output = subprocess.check_output(["iptables", "-S", chain])
            output = output.decode("utf-8")
            return output.split("\n")[0].split(" ")[2]
        return ""

    def match_rule_in_chain(self, chain):
        for num, rule in enumerate(self.tables[chain]):
            target = self.match_rule(rule, chain, num + 1)
            if target:
                if self.tables.get(str(target)) is not None:
                    target = self.match_rule_in_chain(target)
                    if target == "RETURN" or target == False:
                        continue
                elif isinstance(target, dict):
                    if target.get("DNAT"):
                        to_dst = target["DNAT"]["to-destination"].split(":")
                        if to_dst[0]:
                            r["dst"] = to_dst[0]
                        if len(to_dst) == 2:
                            r["dport"] = to_dst[1]
                        return False
                    elif target.get("SNAT"):
                        to_src = target["SNAT"]["to-source"].split(":")
                        if to_src[0]:
                            r["src"] = to_src[0]
                        if len(to_src) == 2:
                            r["sport"] = to_src[1]
                    elif target.get("REDIRECT"):
                        r["dport"] = target["REDIRECT"]["to-ports"]
                return target

        self.data_visualize.append(
            {
                "chain": chain,
                "rule": None,
                "target": self.get_policy(chain),
                "num": None,
                "state": None,
            }
        )

        return False

    def processing(self, chains):
        for chain in chains:
            if chain == "ROUTING":
                chains = self.set_chains()
                return self.processing(chains)
            target = self.match_rule_in_chain(chain)
            if target:
                return True
        return False

    def run(self):
        self.processing(self.chains)
        return self.data_visualize
