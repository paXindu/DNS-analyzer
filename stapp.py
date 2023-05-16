import streamlit as st
import pymongo
from datetime import datetime, timedelta

# Connect to MongoDB
client = pymongo.MongoClient('localhost', 27017)
db = client['DNSdata']
dns_collection = db['DNScapture']

# Calculate the timestamp 10 minutes ago
ten_minutes_ago = datetime.now() - timedelta(minutes=10)

# Fetch documents for the last 10 minutes from MongoDB collection
data = dns_collection.find({"timestamp": {"$gte": ten_minutes_ago}})

# Create a list to store source IPs
source_ip_list = []

# Extract source IPs from the documents
for document in data:
    source_ip_list.append(document['source_ip'])

# Display the source IP list in the browser
st.subheader("Source IPs in the Last 10 Minutes")
if len(source_ip_list) > 0:
    st.write(source_ip_list)
else:
    st.write("No data available for the last 10 minutes.")
