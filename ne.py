from scapy.all import *


def handle_dns_packet(packet):
    try:
        if packet.haslayer(DNSQR):
            query_types = []
            query_sources = []
            dnssec_validation = False
            dns_response_size = 0

            # Get DNS query types
            for qr in packet[DNSQR]:
                query_types.append(qr.qtype)
            print("DNS Query Types: ", query_types)

            # Get DNS query sources
            if packet.haslayer(IP):
                query_sources.append(packet[IP].src)
            elif packet.haslayer(UDP):
                query_sources.append(packet[UDP].sport)
            print("DNS Query Sources: ", query_sources)

            # Check DNSSEC validation
            dnssec_validation = packet[DNS].ad
            print("DNS DNSSEC Validation: ", dnssec_validation)

            # Get DNS response size
            dns_response_size = len(packet[DNSRR])
            print("DNS DNS Response Size: ", dns_response_size)

        else:
            print("Not a DNS query packet.")
    except Exception as e:
        print("Error: " + str(e))


try:
    sniff(filter="udp port 53", prn=handle_dns_packet)
except Exception as e:
    print("Error: " + str(e))
