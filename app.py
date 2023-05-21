from scapy.all import sniff, DNS, IP
from pymongo import MongoClient
from datetime import datetime


client = MongoClient('mongodb://localhost:27017/')
db = client['DNSdata']
collection = db['DNScapture']


collection.create_index("capture_time", expireAfterSeconds=24 * 60 * 60)  


def process_dns_packet(packet):
    if IP in packet and DNS in packet:
        dns = packet[DNS]

        
        cache_hit = dns.an is not None
        query_type = dns.qd.qtype
        response_size = len(dns.an) if dns.an is not None else 0
        response_code = dns.rcode  
        query_latency = packet.time - dns.time
        success = response_code == 0  
        source_ip = packet[IP].src
        query_name = dns.qd.qname.decode()  

        
        document = {
            "capture_time": datetime.now(),
            "cache_hit": cache_hit,
            "query_type": query_type,
            "response_size": response_size,
            "response_code": response_code,
            "query_latency": query_latency,
            "success": success,
            "source_ip": source_ip,
            "query_name": query_name
        }

        
        collection.insert_one(document)

        
        
        print("server runing........")


sniff(filter="udp port 53", prn=process_dns_packet)
