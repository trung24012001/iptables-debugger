from scapy.all import *

dport = 7777
src_ip = "1.2.3.4"
target_ip = "192.168.1.103"

payload = "Hello World"


send(IP(src=src_ip, dst=target_ip) / UDP(dport=dport) / Raw(load=payload))
