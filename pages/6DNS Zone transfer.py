from scapy.all import sniff, DNSRR, DNS
import pandas as pd
import streamlit as st
import altair as alt


dns_data = pd.DataFrame(columns=['Source IP', 'Destination IP', 'Zone'])


def dns_callback(pkt):
    if DNSRR in pkt and pkt[DNS].opcode == 0 and pkt[DNS].ancount > 0:
        for rr in pkt[DNS].an:
            if rr.type == 252:
                source_ip = pkt['IP'].src
                destination_ip = pkt['IP'].dst
                zone = rr.rrname.decode()
                
                dns_data.loc[len(dns_data)] = [source_ip, destination_ip, zone]
                
                st.write("Zone Transfer Detected:")
                st.write(f"Source IP: {source_ip}")
                st.write(f"Destination IP: {destination_ip}")
                st.write(f"Zone: {zone}")
                st.write("---------------------------")


st.set_page_config(page_title='DNS Zone Transfer Analyzer', page_icon=':globe_with_meridians:')


st.write("Sniffing DNS packets...")
sniff(filter="udp port 53", prn=dns_callback)


st.title('DNS Zone Transfer Analysis')
st.write('Zone Transfer information captured from DNS packets')


chart = alt.Chart(dns_data).mark_bar().encode(
    x='count()',
    y=alt.Y('Source IP', sort='-x'),
    tooltip=['Source IP', alt.Tooltip('count()', title='Number of Zone Transfers')]
)


chart = chart.configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_mark(
    tooltip=alt.TooltipContent('encoding')
)


st.altair_chart(chart, use_container_width=True)


st.subheader('DNS Zone Transfer Information')
st.write(dns_data)
