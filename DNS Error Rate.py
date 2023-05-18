import streamlit as st
import pandas as pd
import altair as alt
from pymongo import MongoClient
from datetime import datetime, timedelta

# Connect to the MongoDB database
client = MongoClient('mongodb://localhost:27017')
database = client['DNSdata']
collection = database['DNScapture']

# Specify the time range
selected_range = st.select_slider('Select Time Range (minutes)', options=list(range(1, 61)), value=10)
end_time = collection.find_one(sort=[('_id', -1)])['capture_time']
start_time = end_time - timedelta(minutes=selected_range)

# Define the DNS error response codes and their names
error_codes = {
    1: 'FORMERR: DNS query format error',
    2: 'SERVFAIL: Server failed to complete the DNS request',
    3: 'NXDOMAIN: Domain name does not exist',
    4: 'NOTIMP: Function not implemented',
    5: 'REFUSED: The server refused to answer for the query',
    6: 'YXDOMAIN: Name that should not exist, does exist',
    7: 'XRRSET: RRset that should not exist, does exist',
    8: 'NOTAUTH: Server not authoritative for the zone',
    9: 'NOTZONE: Name not in zone'
}

# Query the database for error responses within the specified time range
query = {
    'capture_time': {
        '$gte': start_time,
        '$lte': end_time
    },
    'response_code': {'$in': list(error_codes.keys())}
}

total_queries = collection.count_documents({'capture_time': {'$gte': start_time, '$lte': end_time}})
error_responses = collection.count_documents(query)
success_queries = total_queries - error_responses

# Calculate DNS error rate and success rate
error_rate = (error_responses / total_queries) * 100
success_rate = (success_queries / total_queries) * 100

# Create a DataFrame for the chart
data = pd.DataFrame({'Error Code': list(error_codes.values()), 'Count': [0] * len(error_codes)})

# Query the database to get the count of each error code
result = collection.aggregate([
    {'$match': query},
    {'$group': {'_id': '$response_code', 'count': {'$sum': 1}}}
])
for entry in result:
    error_code = entry['_id']
    count = entry['count']
    data.loc[data['Error Code'] == error_codes[error_code], 'Count'] = count

# Create the Pie chart-like visualization using mark_arc()
chart = alt.Chart(data).mark_arc().encode(
    color=alt.Color('Error Code', legend=None),
    tooltip=['Error Code', 'Count'],
    theta='Count'
).properties(
    width=500,
    height=500
)

# Display the chart and DNS error rate
st.header('DNS Error Rate')
st.write('Time Range:', start_time, 'to', end_time)
st.write('\n')
st.altair_chart(chart, use_container_width=True)
st.write('Error Rate: {:.2f}%'.format(error_rate))
st.write('Success Rate: {:.2f}%'.format(success_rate))
st.write('\n')

# Display the DNS Error Codes table
st.header('DNS Error Codes')
st.write('Time Range:', start_time, 'to', end_time)
st.write('\n')
st.dataframe(data)
