from scapy.all import sniff, DNS, IP
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['DNSdata']
collection = db['DNScapture']

# Callback function to process DNS packets
def process_dns_packet(packet):
    if IP in packet and DNS in packet:
        dns = packet[DNS]

        # Capture the basic elements
        cache_hit = dns.an is not None
        query_type = dns.qd.qtype
        response_size = len(dns.an) if dns.an is not None else 0
        response_code = dns.rcode  # Renamed error_code to response_code
        query_latency = packet.time - dns.time
        success = response_code == 0  # Set success based on response_code == 0
        source_ip = packet[IP].src
        query_name = dns.qd.qname.decode()  # Decode the DNS query name from bytes to string

        # Create a document to store in MongoDB
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

        # Insert the document into the MongoDB collection
        collection.insert_one(document)

        # Print the captured elements
        print(f"Cache Hit: {cache_hit}")
        print(f"Query Type: {query_type}")
        print(f"Response Size: {response_size}")
        print(f"Response Code: {response_code}")  # Updated print statement
        print(f"Query Latency: {query_latency}")
        print(f"Success: {success}")
        print(f"Source IP: {source_ip}")
        print(f"Query Name: {query_name}")
        print("-----------------------------")

# Sniff DNS packets on the network
sniff(filter="udp port 53", prn=process_dns_packet)
