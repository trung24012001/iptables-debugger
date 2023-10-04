import iptc
import ipaddress
import os
import uuid
import subprocess
from netifaces import ifaddresses, interfaces, AF_INET
from nsenter import Namespace


class IptablesHandler:
    def __init__(self):
        self.addrinf = self.get_addrinf()
        self.tables = self.init_tables()
        self.packet = {}
        self.results = []

    def import_packet(self, packet):
        self.packet = packet
        chains = self.init_chains()
        self.processing(chains)
        return self.results

    def init_chains(self):
        chains = ["RAW_PREROUTING", "MANGLE_PREROUTING", "NAT_PREROUTING", "ROUTING"]
        #if self.addrinf.get(self.packet["saddr"]):
        if self.packet["outinf"]:
            chains = ["RAW_OUTPUT", "MANGLE_OUTPUT", "NAT_OUTPUT", "FILTER_OUTPUT", "MANGLE_POSTROUTING", "NAT_POSTROUTING"]
            #self.packet["outinf"] = self.addrinf[self.packet["saddr"]]
        #elif self.addrinf.get(self.packet["daddr"]):
        #    self.packet["ininf"] = self.addrinf[self.packet["daddr"]]
        return chains

    def init_tables(self):
        raws = iptc.easy.dump_table("raw")
        mangles = iptc.easy.dump_table("mangle")
        nats = iptc.easy.dump_table("nat")
        filters = iptc.easy.dump_table("filter")
        tables = {}
        for chain in raws:
            tables[f"RAW_{chain}"] = raws[chain]
        for chain in mangles:
            tables[f"MANGLE_{chain}"] = mangles[chain]
        for chain in nats:
            tables[f"NAT_{chain}"] = nats[chain]
        for chain in filters:
            tables[f"FILTER_{chain}"] = filters[chain]

        return tables


    def get_addrinf(self):
        addrinf = {}
        for ifaceName in interfaces():
            for inf in ifaddresses(ifaceName).setdefault(AF_INET, [{"addr": None}]):
                addr = inf["addr"]
                if addr:
                    addrinf[addr] = ifaceName
        return addrinf

    def get_bridges(self, inf):
        try:
            path = "/sys/class/net/{}/brif/".format(inf)
            return os.listdir(path)
        except:
            return []

    def set_chains(self):
        chains = ["MANGLE_FORWARD", "FILTER_FORWARD", "MANGLE_POSTROUTING", "NAT_POSTROUTING"]
        if self.addrinf.get(self.packet["saddr"]):
            chains = ["RAW_OUTPUT", "MANGLE_OUTPUT", "NAT_OUTPUT", "FILTER_OUTPUT", "MANGLE_POSTROUTING", "NAT_POSTROUTING"]
        elif self.addrinf.get(self.packet["daddr"]):
            chains = ["MANGLE_INPUT", "NAT_INPUT", "FILTER_INPUT"]
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
            return None
        if port.find(":") != -1:
            port = range(*list(map(lambda p: int(p), port.split(":"))))
        else:
            port = [int(port)]
        return port

    def parse_inf(self, inf):
        if inf == None:
            return None
        if inf.find("!") >= 0:
            tmp = inf.split("!")[1]
            inf = interfaces()
            inf.remove(tmp)
        else:
            inf = [inf]
        return inf

    def handle_addr(self, p_addr, addr):
        if not p_addr:
            return False
        p_addr = ipaddress.ip_address(p_addr)
        if isinstance(addr, list):
            for item in addr:
                if p_addr in item:
                    return True
            return False
        elif p_addr not in addr:
            return False
        return True

    def handle_prot(self, p_prot, p_sport, p_dport, prot, rule):
        print(p_dport, prot, rule)
        if prot == None:
            return True
        if p_prot != prot:
            return False
        port = rule.get(p_prot)
        if port == None:
            return True
        sport = self.parse_port(port.get("sport"))
        dport = self.parse_port(port.get("dport"))
        if sport:
            if not p_sport:
                return False
            if int(p_sport) not in sport:
                return False
        if dport:
            if not p_dport:
                return False
            if int(p_dport) not in dport:
                return False
        return True

    def handle_inf(self, p_inf, inf):
        if inf == None:
            return True
        if p_inf not in inf:
            return False
        return True
    
    def handle_mac(self, p_smac, p_dmac, mac):
        if mac == None:
            return True
        smac = mac.get("mac-source")
        dmac = mac.get("mac-destination")
        if smac:
            if not p_smac:
                return False
            if isinstance(smac, list):
                if p_smac == smac[1]:
                    return False
            elif p_mac != smac:
                return False
        if dmac:
            if not p_dmac:
                return False
            if isinstance(dmac, list):
                if p_dmac == dmac[1]:
                    return False
            elif p_dmac != dmac:
                return False
        return True


    def handle_physdev(self, p_ininf, p_outinf, physdev):
        if physdev == None:
            return True
        phys_in = physdev.get("physdev-in")
        phys_out = physdev.get("physdev-out")
        if phys_in:
            if not p_ininf:
                return False
            if phys_in not in self.get_bridges(p_ininf):
                return False
        if phys_out:
            if not p_outinf:
                return False
            if phys_out not in self.get_bridges(p_outinf):
                return False
        return True

    def handle_mark(self, p_mark, mark):
        if mark == None:
            return True
        return True

    def handle_state(self, p_state, state):
        if state == None:
            return True
        states = (state.get("state") or state.get("ctstate")).split(",")
        if p_state not in states:
            return False
        return True

    def match_rule(self, rule, chain, num):
        saddr = self.parse_addr(rule.get("src"))
        daddr = self.parse_addr(rule.get("dst"))
        ininf = self.parse_inf(rule.get("in-interface"))
        outinf = self.parse_inf(rule.get("out-interface"))
        mac = rule.get("mac")
        prot = rule.get("protocol")
        target = rule.get("target")
        physdev = rule.get("physdev")
        mark = rule.get("mark")
        state = rule.get("state") or rule.get("conntrack")

        if not self.handle_addr(self.packet["saddr"], saddr):
            return False
        if not self.handle_addr(self.packet["daddr"], daddr):
            return False
        if not self.handle_inf(self.packet["ininf"], ininf):
            return False
        if not self.handle_inf(self.packet["outinf"], outinf):
            return False
        if not self.handle_prot(self.packet["prot"], self.packet["sport"], self.packet["dport"], prot, rule):
            return False
        if not self.handle_mac(self.packet["smac"], self.packet["dmac"], mac):
            return False
        if not self.handle_physdev(self.packet["ininf"], self.packet["outinf"], physdev):
            return False
        if not self.handle_mark(self.packet["mark"], mark):
            return False
        if not self.handle_state(self.packet["state"], state):
            return False

        table_name, chain_name = self.split_chain(chain) 

        self.results.append(
            {
                "table": table_name,
                "chain": chain_name, 
                "rule": rule, 
                "target": target, 
                "num": num, 
                "state": state
            }
        )

        return target

    def get_policy(self, chain):
        if chain in ["PREROUTING", "POSTROUTING"]:
            return "ACCEPT"
        elif chain in ["INPUT", "FORWARD", "OUTPUT"]:
            output = subprocess.check_output(["iptables", "-S", chain])
            output = output.decode("utf-8")
            return output.split("\n")[0].split(" ")[2]
        return ""

    def split_chain(self, chain):
        table_name = chain.split("_")[0]
        chain_name = chain.split("_")[1]
        return (table_name, chain_name)

    def matching(self, chain):
        table_name, chain_name = self.split_chain(chain) 
        for num, rule in enumerate(self.tables[chain]):
            target = self.match_rule(rule, chain, num + 1)
            if not target:
                continue
            user_chain = f"{table_name}_{target}"
            if self.tables.get(user_chain) != None:
                target = self.match_rule_in_chain(user_chain)
                if target == "RETURN" or target == False:
                    continue
            elif isinstance(target, dict):
                if target.get("DNAT"):
                    to_dst = target["DNAT"]["to-destination"].split(":")
                    if to_dst[0]:
                        self.packet["daddr"] = to_dst[0]
                    if len(to_dst) == 2:
                        self.packet["dport"] = to_dst[1]
                elif target.get("SNAT"):
                    to_src = target["SNAT"]["to-source"].split(":")
                    if to_src[0]:
                        self.packet["saddr"] = to_src[0]
                    if len(to_src) == 2:
                        self.packet["sport"] = to_src[1]
                elif target.get("REDIRECT"):
                    self.packet["dport"] = target["REDIRECT"]["to-ports"]
            return target
        return None

    def match_rule_in_chain(self, chain):
        table_name, chain_name = self.split_chain(chain) 

        if table_name == "NAT" and self.packet["state"] != "NEW":
            return False

        target = self.matching(chain)
        
        if target == "RETURN" or target == None:
            self.results.append(
                {
                    "table": table_name,
                    "chain": chain_name,
                    "rule": None,
                    "target": self.get_policy(chain_name),
                    "num": None,
                    "state": None,
                }
            )
            return False

        return target

    def processing(self, chains):
        for chain in chains:
            if chain == "ROUTING":
                new_chains = self.set_chains()
                return self.processing(new_chains)
            target = self.match_rule_in_chain(chain)
            if target in ["ACCEPT", "DROP", "REJECT"]:
                return True
        return False
