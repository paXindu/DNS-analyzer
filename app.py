from scapy.layers.inet import IP
from scapy.layers.dns import DNS, DNSRR, DNSQR
from scapy.sendrecv import sniff
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

    query_types = []

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

                    if packet[DNS].qr == 1 and packet[DNS].opcode == 6:  # "IXFR" opcode is represented by 6
                        zone_transfer_count += 1

                if packet.haslayer(DNSQR):
                    for qr in packet[DNSQR]:
                        query_types.append(str(qr))

                dnssec_validation = packet[DNS].ad if DNS in packet else False
                dns_response_size = len(packet[DNSRR]) if DNSRR in packet else 0

                dns_packet = packet[DNS]
                dns_message_type = dns_packet.qr
                dns_response_code = dns_packet.rcode
                dns_query_id = dns_packet.id
                dns_question_section = str(dns_packet.qd)
                dns_answer_section = str(dns_packet.an)
                dns_authority_section = str(dns_packet.ns)
                dns_additional_section = str(dns_packet.ar)

                packet_data = {
                    "source_ip": src_ip,
                    "query_count": query_count,
                    "response_time_avg": total_response_time / query_count if query_count > 0 else 0,
                    "error_rate": error_count / query_count * 100 if query_count > 0 else 0,
                    "cache_hit_rate": cache_hit_count / query_count * 100 if query_count > 0 else 0,
                    "zone_transfer_activity": zone_transfer_count,
                    "dns_query_types": query_types,
                    "dnssec_validation": dnssec_validation,
                    "dns_response_size": dns_response_size,
                    "dns_message_type": dns_message_type,
                    "dns_response_code": dns_response_code,
                    "dns_query_id": dns_query_id,
                    "dns_question_section": dns_question_section,
                    "dns_answer_section": dns_answer_section,
                    "dns_authority_section": dns_authority_section,
                    "dns_additional_section": dns_additional_section
                }

                dns_collection.insert_one(packet_data)

                print("Query Volume: {}".format(query_count))
                if query_count > 0:
                    print("Response Time (avg): {:.2f} seconds".format(total_response_time / query_count))
                    print("Error Rate: {:.2f}%".format(error_count / query_count * 100))
                    print("Cache Hit Rate: {:.2f}%".format(cache_hit_count / query_count * 100))
                    print("DNS Zone Transfer Activity: {}".format(zone_transfer_count))
                    print("DNS Query Types:", query_types)
                    print("DNS DNSSEC Validation:", dnssec_validation)
                    print("DNS DNS Response Size:", dns_response_size)
                    print("DNS Message Type:", dns_message_type)
                    print("DNS Response Code:", dns_response_code)
                    print("DNS Query ID:", dns_query_id)
                    print("DNS Question Section:", dns_question_section)
                    print("DNS Answer Section:", dns_answer_section)
                    print("DNS Authority Section:", dns_authority_section)
                    print("DNS Additional Section:", dns_additional_section)


def main():
    sniff(filter=DNS_FILTER, prn=analyze_packet)

if __name__ == "__main__":
    main()
                   
