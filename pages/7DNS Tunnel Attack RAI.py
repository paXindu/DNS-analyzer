import pickle
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from scapy.layers.dns import DNSQR
from scapy.all import sniff

st.title("DNS tunnel detection")

vectorizer = pickle.load(open("./vectorizer.pkl", 'rb'))
DNSmodel = pickle.load(open("./DNSmodel.pkl", 'rb'))


def dns_packet(packet):
    if packet.haslayer(DNSQR):
        query = packet[DNSQR].qname.decode()
        st.write("Query: ", query)
        X_new = vectorizer.transform([query])
        pred = DNSmodel.predict(X_new)[0]
        accuracy = DNSmodel.predict_proba(X_new)[0][pred]
        if pred == 0:
            st.write(
                "Regular domain name with {:.2f}% accuracy".format(accuracy*100))
        else:
            st.write(
                "Domain name with tunnel with {:.2f}% accuracy".format(accuracy*100))


def start_sniffing():
    st.write("Starting packet sniffing...")
    sniff(filter="udp and port 53", prn=dns_packet)


if st.button("Start"):
    start_sniffing()
