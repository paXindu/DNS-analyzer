import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

mongodb_url = 'mongodb://localhost:27017'
database_name = 'DNSdata'
collection_name = 'DNScapture'

client = MongoClient(mongodb_url)
database = client[database_name]
collection = database[collection_name]

st.title('DNS Cache Hit Rate Calculator')
st.write('Calculate the cache hit rate for a specified time range')

time_ranges = {
    'Last 1 minute': 1,
    'Last 5 minutes': 5,
    'Last 30 minutes': 30,
    'Last 60 minutes': 60
}

selected_range = st.slider('Select Time Range (minutes)', 1, 200, 10)

end_time = collection.find_one(sort=[('_id', -1)])['capture_time']
start_time = end_time - timedelta(minutes=selected_range)

query = {'capture_time': {'$gte': start_time, '$lt': end_time}}
dns_data = collection.find(query)

timestamps = []
hit_rates = []
total_dns_queries = 0
cached_dns_queries = 0

for entry in dns_data:
    total_dns_queries += 1
    if entry['cache_hit']:
        cached_dns_queries += 1
    timestamps.append(entry['capture_time'])
    hit_rates.append((cached_dns_queries / total_dns_queries) * 100)

data = {'Timestamp': timestamps, 'Hit Rate': hit_rates}
df = pd.DataFrame(data)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df['Timestamp'], df['Hit Rate'])
ax.set_xlabel('Timestamp')
ax.set_ylabel('Hit Rate')
ax.set_title(f'Cache Hit Rate over Time ({selected_range} minutes)')
ax.grid(True)

st.pyplot(fig)

st.write(f"Cache Hit Rate for the last {selected_range} minutes: {hit_rates[-1]:.2f}%")

client.close()
