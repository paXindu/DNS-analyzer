from scapy.all import *
from pymongo import MongoClient


DNS_PORT = 53


DNS_FILTER = "udp port {}".format(DNS_PORT)


query_count = 0
total_response_time = 0


error_count = 0
cache_hit_count = 0


zone_transfer_count = 0


client = MongoClient('localhost', 27017)
db = client['DNSdata']
dns_collection = db['DNScapture']


def analyze_packet(packet):
    global query_count, total_response_time, error_count, cache_hit_count, zone_transfer_count

    if IP in packet:

        src_ip = packet[IP].src

        if DNS in packet:

            query_count += 1

            if packet.haslayer(DNSRR):

                response_time = packet.time - packet[DNS].id
                total_response_time += response_time

                if packet[DNS].rcode != 0:
                    error_count += 1
                else:

                    if packet.an is not None and packet.an.rrname == packet[DNSQR].qname:
                        cache_hit_count += 1

                    if packet[DNS].qr == 1 and packet[DNS].opcode == "IXFR":
                        zone_transfer_count += 1

            packet_data = {
                "source_ip": src_ip,
                "query_count": query_count,
                "response_time_avg": total_response_time / query_count if query_count > 0 else 0,
                "error_rate": error_count / query_count * 100 if query_count > 0 else 0,
                "cache_hit_rate": cache_hit_count / query_count * 100 if query_count > 0 else 0,
                "zone_transfer_activity": zone_transfer_count
            }

            dns_collection.insert_one(packet_data)

    print("Query Volume: {}".format(query_count))
    if query_count > 0:
        print("Response Time (avg): {:.2f} seconds".format(
            total_response_time / query_count))
        print("Error Rate: {:.2f}%".format(error_count / query_count * 100))
        print("Cache Hit Rate: {:.2f}%".format(
            cache_hit_count / query_count * 100))
        print("DNS Zone Transfer Activity: {}".format(zone_transfer_count))


sniff(filter=DNS_FILTER, prn=analyze_packet)
