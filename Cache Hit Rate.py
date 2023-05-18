import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# Specify the MongoDB connection details
mongodb_url = 'mongodb://localhost:27017'  # Replace with your MongoDB connection URL
database_name = 'DNSdata'  # Replace with your database name
collection_name = 'DNScapture'  # Replace with your collection name

# Connect to MongoDB and retrieve the collection
client = MongoClient(mongodb_url)
database = client[database_name]
collection = database[collection_name]

# Title and description for the web app
st.title('DNS Cache Hit Rate Calculator')
st.write('Calculate the cache hit rate for a specified time range')

# Define the time range options
time_ranges = {
    'Last 1 minute': 1,
    'Last 5 minutes': 5,
    'Last 30 minutes': 30,
    'Last 60 minutes': 60
}

# Dropdown menu to select the time range
selected_range = st.selectbox('Select Time Range', list(time_ranges.keys()))

# Calculate the start and end times based on the selected range
end_time = collection.find_one(sort=[('_id', -1)])['capture_time']
start_time = end_time - timedelta(minutes=time_ranges[selected_range])

# Query the database for DNS data within the specified time range
query = {'capture_time': {'$gte': start_time, '$lt': end_time}}
dns_data = collection.find(query)

# Initialize variables for hit rate calculation
timestamps = []
hit_rates = []
total_dns_queries = 0
cached_dns_queries = 0

# Iterate through the DNS data and count the total and cached queries
for entry in dns_data:
    total_dns_queries += 1
    if entry['cache_hit']:
        cached_dns_queries += 1
    timestamps.append(entry['capture_time'])
    hit_rates.append((cached_dns_queries / total_dns_queries) * 100)

# Create a DataFrame with timestamps and hit rates
data = {'Timestamp': timestamps, 'Hit Rate': hit_rates}
df = pd.DataFrame(data)

# Create a line chart
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df['Timestamp'], df['Hit Rate'])
ax.set_xlabel('Timestamp')
ax.set_ylabel('Hit Rate')
ax.set_title(f'Cache Hit Rate over Time ({selected_range})')
ax.grid(True)

# Display the line chart
st.pyplot(fig)

# Display the cache hit rate and selected time range
st.write(f"Cache Hit Rate for the last {selected_range}: {hit_rates[-1]:.2f}%")

# Close the MongoDB connection
client.close()
