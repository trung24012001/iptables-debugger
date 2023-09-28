import iptc
import ipaddress
import os
import uuid
import subprocess
from netifaces import ifaddresses, interfaces, AF_INET


class IptablesHandler:
    def __init__(self):
        self.addrInf = self.get_addrinf()
        self.tables = self.init_tables()
        self.chains = []
        self.packet = {}
        self.results = []

    def import_packet(self, packet):
        self.packet = packet
        self.chains = self.init_chains()
        self.processing(self.chains)
        return self.results

    def init_chains(self):
        chains = ["PREROUTING", "ROUTING"]
        if self.addrInf.get(self.packet["dst"]):
            chains = ["OUTPUT", "POSTROUTING"]
            self.packet["outif"] = self.addrInf[self.packet["src"]]
        elif self.addrInf.get(self.packet["dst"]):
            self.packet["inif"] = self.addrInf[self.packet["dst"]]
        return chains

    def init_tables(self):
        raws = iptc.easy.dump_table("raw")
        mangles = iptc.easy.dump_table("mangle")
        nats = iptc.easy.dump_table("nat")
        filters = iptc.easy.dump_table("filter")
        chains = ["PREROUTING", "INPUT", "FORWARD", "OUTPUT", "POSTROUTING"]
        tables = {}
        for chain in chains:
            tables[chain] = []
            if raws.get(chain):
                tables[chain] += raws.get(chain)
            if mangles.get(chain):
                tables[chain] += mangles.get(chain)
            if nats.get(chain):
                tables[chain] += nats.get(chain)
            if filters.get(chain):
                tables[chain] += filters.get(chain)
        return tables


    def get_addrinf(self):
        addrInf = {}
        for ifaceName in interfaces():
            for inf in ifaddresses(ifaceName).setdefault(AF_INET, [{"addr": None}]):
                addr = inf["addr"]
                if addr:
                    addrInf[addr] = ifaceName
        return addrInf

    def get_bridges(inf):
        path = "/sys/class/net/{}/brif/".format(inf)
        return os.listdir(path)

    def set_chains(self):
        if self.addrInf.get(self.packet["src"]):
            chains = ["OUTPUT", "POSTROUTING"]
        elif self.addrInf.get(self.packet["dst"]):
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
        port = rule.get(self.packet["prot"])
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

    def handle_inf(self, pinf, inf):
        if inf == "*":
            return True
        if pinf not in inf:
            return False
        return True

    def handle_physdev(self, pinif, poutif, physdev):
        if physdev == None:
            return True
        phys_in = physdev.get("physdev-in")
        phys_out = physdev.get("physdev-out")
        is_match = False
        if phys_in:
            if pifin == None:
                return False
            else:
                if phys_in in self.get_bridges(pinif):
                    is_match = True
                else:
                    is_match = False
        if phys_out:
            if poutif == None:
                return False
            else:
                if phys_out in self.get_bridges(poutif):
                    is_match = True
                else:
                    is_match = False
        return is_match

    def handle_mark(self, mark):
        # I will handle this later
        if mark == None:
            return True
        return False

    def handle_state(self, pstate, state):
        if pstate == "*" or state == None:
            return True
        states = (state.get("state") or state.get("ctstate")).split(",")
        if rstate not in states:
            return False
        return True

    def match_rule(self, rule, chain, num):
        src = self.parse_addr(rule.get("src"))
        dst = self.parse_addr(rule.get("dst"))
        inif = self.parse_inf(rule.get("in-interface"))
        outif = self.parse_inf(rule.get("out-interface"))
        prot = rule.get("protocol")
        target = rule.get("target")
        physdev = rule.get("physdev")
        mark = rule.get("mark")
        state = rule.get("state") or rule.get("conntrack")

        if not self.handle_address(self.packet["src"], src):
            return False
        if not self.handle_address(self.packet["dst"], dst):
            return False
        if not self.handle_prot(self.packet["prot"], self.packet["sport"], self.packet["dport"], prot, rule):
            return False
        if not self.handle_inf(self.packet["inif"], inif):
            return False
        if not self.handle_inf(self.packet["outif"], outif):
            return False
        if not self.handle_physdev(self.packet["inif"], self.packet["outif"], physdev):
            return False
        if not self.handle_mark(mark):
            return False
        if not self.handle_state(self.packet["state"], state):
            return False

        self.results.append(
            {
                "chain": chain, 
                "rule": rule, 
                "target": target, 
                "num": num, 
                "state": state
            }
        )

        return target

    def get_policy(chain):
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
                            self.packet["dst"] = to_dst[0]
                        if len(to_dst) == 2:
                            self.packet["dport"] = to_dst[1]
                        return False
                    elif target.get("SNAT"):
                        to_src = target["SNAT"]["to-source"].split(":")
                        if to_src[0]:
                            self.packet["src"] = to_src[0]
                        if len(to_src) == 2:
                            self.packet["sport"] = to_src[1]
                    elif target.get("REDIRECT"):
                        self.packet["dport"] = target["REDIRECT"]["to-ports"]
                return target

        self.results.append(
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
