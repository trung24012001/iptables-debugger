import iptc
import ipaddress
import argparse
import os
from netifaces import ifaddresses, interfaces, AF_INET
from tabulate import tabulate


parser = argparse.ArgumentParser(description='Iptables debugger tool')
parser.add_argument('-s', '--src', default='*',
                        help='source address, default=*')
parser.add_argument('-d', '--dst', default='*',
                        help='destination address, default=*')
parser.add_argument('--sport', default='*',
                        help='source port, default=*')
parser.add_argument('--dport', default='*',
                        help='destination port, default=*')
parser.add_argument('-p', '--protocol', default='*',
                        help='protocol, default=*')
parser.add_argument('--state', default='*',
                        help='state, default=*')
parser.add_argument('-m', '--mark', default='*',
                        help='mark, default=*')
parser.add_argument('-v', '--visualize', action='count', default=0,
                        help='-vv for more, enable visualization')

args = parser.parse_args()
#if 'protocol' not in vars(args) and ('dport' in vars(args) or 'sport' in vars(args)):
#    parser.error('The --sport and --dport argument requires the --protocol')  

tables = iptc.easy.dump_table('nat')
filters = iptc.easy.dump_table('filter')
for chain in filters:
    tables[chain] = filters[chain]
#    if chain not in tables:
#        tables[chain] = filters[chain]
#    else:
#        for rule in filters[chain]:
#            tables[chain].append(rule)

r = {'src': args.src, 'sport': args.sport, 'dst': args.dst, 'dport': args.dport, 'prot': args.protocol, 'in_inf': None, 'out_inf': None, 'state': args.state}
data_visualize = []

def get_addresses():
    addresses = []
    addrInf = {}
    for ifaceName in interfaces():
        for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr': None}]):
            addr = i['addr']
            if addr:
                addresses.append(addr)
                addrInf[addr] = ifaceName
    return addresses, addrInf

addrs, addrInf = get_addresses()

if r['src'] in addrs:
    chains = ['OUTPUT', 'POSTROUTING']
    r['out_inf'] = addrInf[r['src']]
elif r['dst'] in addrs:
    chains = ['PREROUTING', 'ROUTING']
    r['in_inf'] = addrInf[r['dst']]
else:
    chains = ['PREROUTING', 'ROUTING']    

def get_bridges(inf):
    path = '/sys/class/net/{}/brif/'.format(inf)
    return os.listdir(path)

def set_chains():
    if r['src'] in addrs:
        chains = ['OUTPUT', 'POSTROUTING']
    elif r['dst'] in addrs:
        chains = ['INPUT']
    else:
        chains = ['FORWARD', 'POSTROUTING']
    return chains

def parse_addr(addr):
    if addr == None:
        addr = '0.0.0.0/0'
    elif addr.find('/') == -1:
        addr += '/32'
    if addr.find('!') != -1:
        addr = addr.split('!')[1]
        return list(ipaddress.ip_network(u'0.0.0.0/0').address_exclude(ipaddress.ip_network(unicode(addr))))
    return ipaddress.ip_network(unicode(addr))

def parse_port(port):
    if port == None:
        port = '*'
    elif port.find(':') != -1:
        port = range(*list(map(lambda p: int(p), port.split(':'))))
    else:
        port = [int(port)]
    return port

def parse_inf(inf):
    if inf == None:
        inf = '*'
    elif inf.find('!') != -1:
        tmp = inf.split('!')[1]
        inf = interfaces()
        inf.remove(tmp)
    else:
        inf = [inf]
    return inf

def handle_address(rsrc, src):
    if rsrc == '*':
        return True
    rsrc = ipaddress.ip_address(unicode(rsrc))
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

def handle_prot(rprot, prot):
    if rprot == '*' or prot == None:
        return True
    if rprot != prot:
        return False
    return True

def handle_port(rsport, rdport, prot, rule):
    if prot == None:
        return True
    port = rule.get(prot)
    if port:
        sport = parse_port(port.get('sport'))
        dport = parse_port(port.get('dport'))
        if rsport != '*' and sport != '*':
            if int(rsport) not in sport:
                return False
        if rdport != '*' and dport != '*':
            if int(rdport) not in dport:
                return False
    return True

def handle_inf(rinf, inf):
    if inf == '*':
        return True
    if rinf not in inf:
        return False
    return True

def handle_physdev(rinf_in, rinf_out, physdev):
    if physdev == None:
        return True
    phys_in = physdev.get('physdev-in')
    phys_out = physdev.get('physdev-out')
    is_match = False
    if phys_in:
        if rinf_in == None:
            return False
        else:
            if phys_in in get_bridges(rinf_in):
                is_match = True
            else:
                is_match = False
    if phys_out:
        if rinf_out == None:
            return False
        else:
            if phys_out in get_bridges(rinf_out):
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
    if rstate == '*' or state == None:
        return True
    states = (state.get('state') or state.get('ctstate')).split(',')
    if rstate not in states:
        return False
    return True


def match_rule(rule, chain, num):
    src = parse_addr(rule.get('src'))
    dst = parse_addr(rule.get('dst'))
    inInf = parse_inf(rule.get('in-interface'))
    outInf = parse_inf(rule.get('out-interface'))
    prot = rule.get('protocol')
    target = rule.get('target')
    physdev = rule.get('physdev')
    mark = rule.get('mark')
    state = rule.get('state') or rule.get('conntrack')

    if not handle_address(r['src'], src):
        return False
    if not handle_address(r['dst'], dst):
        return False
    if not handle_prot(r['prot'], prot):
        return False
    if not handle_port(r['sport'], r['dport'], prot, rule):
        return False
    if not handle_inf(r['in_inf'], inInf):
        return False
    if not handle_inf(r['out_inf'], outInf):
        return False
    if not handle_physdev(r['in_inf'], r['out_inf'], physdev):
        return False
    if not handle_mark(mark):
        return False
    if not handle_state(r['state'], state):
        return False

    data_visualize.append({'chain': chain, 'rule': rule, 'target': target, 'num': num, 'state': state})  

    return target

def get_policy(chain):
    import subprocess
    if chain in ['PREROUTING', 'POSTROUTING']:
        return 'ACCEPT'
    elif chain in ['INPUT', 'FORWARD', 'OUTPUT']:
        output = subprocess.check_output(['iptables', '-S', chain]).decode('utf-8')
        return output.split('\n')[0].split(' ')[2]
    return ''

def match_rule_in_chain(chain):
    for num, rule in enumerate(tables[chain]):
        target = match_rule(rule, chain, num + 1)
        if target:
            if tables.get(str(target)) is not None:
                target = match_rule_in_chain(target)
                if target == 'RETURN' or target == False:
                    continue
            elif isinstance(target, dict):
                if target.get('DNAT'):
                    to_dst = target['DNAT']['to-destination'].split(':')
                    if to_dst[0]:
                        r['dst'] = to_dst[0]
                    if len(to_dst) == 2:
                        r['dport'] = to_dst[1] 
                    return False
                elif target.get('SNAT'):
                    to_src = target['SNAT']['to-source'].split(':')
                    if to_src[0]:
                        r['src'] = to_src[0]
                    if len(to_src) == 2:
                        r['sport'] = to_src[1]
                elif target.get('REDIRECT'):
                    r['dport'] = target['REDIRECT']['to-ports']
            return target
    
    data_visualize.append({'chain': chain, 'rule': None, 'target': get_policy(chain), 'num': None, 'state': None})

    return False


def processing(chains):
    for chain in chains:
        if chain == 'ROUTING':
            chains = set_chains()
            return processing(chains)
        target = match_rule_in_chain(chain)
        if target:
            return True
    return False


def visualize():
    table = []
    for data in data_visualize:
        num = data['num'] or 'default'
        pkts = None
        chain = data['chain']
        prot = None
        in_inf = None
        out_inf = None
        src = None
        sport = None
        dst = None
        dport = None
        target = data['target']
        state = data['state']

        rule = data.get('rule')
        if rule:
            prot = rule.get('protocol') or '*'
            sport = '*'
            dport = '*'
            if prot != '*':
                port = rule.get(prot)
                if port:
                    sport = port.get('sport') or '*'
                    dport = port.get('dport') or '*'
            
            pkts = rule['counters'][0]
            in_inf = rule.get('in-interface') or '*'
            out_inf = rule.get('out-interface') or '*'
            src = rule.get('src') or '0.0.0.0/0'
            dst = rule.get('dst') or '0.0.0.0/0'

        row = [chain, prot, in_inf, out_inf, src, sport, dst, dport, target]
        if args.visualize > 1:
            row = [num, pkts] + row
        if args.visualize > 2:
            row.append(state)
        table.append(row)

    headers = ['chain', 'prot', 'in', 'out', 'src', 'sport', 'dst', 'dport', 'target']
    if args.visualize > 1:
        headers = ['num', 'pkts'] + headers
    if args.visualize > 2:
        headers.append('state')

    print(tabulate(table, headers, tablefmt='psql'))


def main():               
    processing(chains)
    if args.visualize > 0:
        visualize()
main()
