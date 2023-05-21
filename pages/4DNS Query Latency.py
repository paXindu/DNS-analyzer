import streamlit as st
import pandas as pd
import altair as alt
from pymongo import MongoClient
from datetime import datetime, timedelta


client = MongoClient('mongodb://localhost:27017')
database = client['DNSdata']
collection = database['DNScapture']


current_time = datetime.now()


selected_range = st.select_slider('Select Time Range (minutes)', options=list(range(1, 200)), value=10)
end_time = collection.find_one(sort=[('_id', -1)])['capture_time']
start_time = end_time - timedelta(minutes=selected_range)


query = {
    'capture_time': {
        '$gte': start_time,
        '$lte': end_time
    }
}
data = list(collection.find(query, {'_id': 0, 'capture_time': 1, 'query_latency': 1}))


df = pd.DataFrame(data)


df = df.dropna(subset=['query_latency'])


line_chart = alt.Chart(df).mark_line().encode(
    x='capture_time:T',
    y='query_latency:Q'
)


line_chart = line_chart.configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_mark(
    tooltip=alt.TooltipContent('encoding')
)


st.title('Query Latency')
st.write('Line chart of query latency over time')
st.write('Time Range:', start_time, 'to', end_time)
st.altair_chart(line_chart, use_container_width=True)
