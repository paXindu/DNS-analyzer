import streamlit as st
import pandas as pd
import altair as alt
from pymongo import MongoClient
from datetime import datetime, timedelta

# Connect to the MongoDB database
client = MongoClient('mongodb://localhost:27017')
database = client['DNSdata']
collection = database['DNScapture']

# Query type mapping dictionary
query_type_mapping = {
    1: 'A (Address)',
    28: 'AAAA (IPv6 Address)',
    5: 'CNAME (Canonical Name)',
    15: 'MX (Mail Exchanger)',
    2: 'NS (Name Server)',
    12: 'PTR (Pointer)',
    6: 'SOA (Start of Authority)',
    16: 'TXT (Text)',
    33: 'SRV (Service)'
}

# Specify the time range
selected_range = st.select_slider('Select Time Range (minutes)', options=list(range(1, 61)), value=10)
end_time = collection.find_one(sort=[('_id', -1)])['capture_time']
start_time = end_time - timedelta(minutes=selected_range)

# Query the database for the desired time range and count the occurrences of each query_type
query = {
    'capture_time': {
        '$gte': start_time,
        '$lte': end_time
    }
}

result_occurrences = list(collection.aggregate([
    {'$match': query},
    {'$group': {'_id': '$query_type', 'count': {'$sum': 1}}}
]))

# Prepare the data for the occurrences bar chart
data_occurrences = []
for entry in result_occurrences:
    query_type = entry['_id']
    count = entry['count']
    query_type_name = query_type_mapping.get(query_type, 'Unknown')
    data_occurrences.append({'Query Type': query_type_name, 'Occurrences': count})

df_occurrences = pd.DataFrame(data_occurrences)

# Create the occurrences bar chart
chart_occurrences = alt.Chart(df_occurrences).mark_bar().encode(
    x='Occurrences',
    y=alt.Y('Query Type', sort='-x')
)

# Display the occurrences bar chart in Streamlit
st.header('DNS Query Types')
st.write('Time Range:', start_time, 'to', end_time)
st.write('\n')
st.altair_chart(chart_occurrences, use_container_width=True)

# Display the query types and their occurrences
st.subheader('Query Types and Occurrences')
for entry in result_occurrences:
    query_type = entry['_id']
    count = entry['count']
    query_type_name = query_type_mapping.get(query_type, 'Unknown')
    st.write(f"{query_type_name}: {count} occurrences")

# Query the database for the desired time range and retrieve the capture time and response size
query_response_size = {
    'capture_time': {
        '$gte': start_time,
        '$lte': end_time
    },
    'response_size': {'$exists': True}  # Filter for documents with response_size field
}

result_response_size = list(collection.find(query_response_size, {'capture_time': 1, 'response_size': 1}).sort('capture_time'))

# Prepare the data for the line chart
data_response_size = []
for entry in result_response_size:
    capture_time = entry['capture_time']
    response_size = entry['response_size']
    data_response_size.append({'Capture Time': capture_time, 'Response Size': response_size})

df_response_size = pd.DataFrame(data_response_size)

# Create the line chart
chart_response_size = alt.Chart(df_response_size).mark_line().encode(
    x='Capture Time:T',
    y='Response Size:Q',
    tooltip=['Capture Time:T', 'Response Size:Q']
).interactive()

# Display the line chart in Streamlit
st.header('DNS Response Size over Time')
st.write('Time Range:', start_time, 'to', end_time)
st.write('\n')
st.altair_chart(chart_response_size, use_container_width=True)


