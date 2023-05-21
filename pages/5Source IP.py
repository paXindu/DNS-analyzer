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
data = list(collection.find(query, {'_id': 0, 'capture_time': 1, 'source_ip': 1}))


df = pd.DataFrame(data)


grouped_df = df.groupby('source_ip').size().reset_index(name='count')
grouped_df = grouped_df.sort_values(by='count', ascending=False)


bar_chart = alt.Chart(grouped_df).mark_bar().encode(
    x='count:Q',
    y=alt.Y('source_ip:N', sort='-x')
)


bar_chart = bar_chart.configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_mark(
    tooltip=alt.TooltipContent('encoding')
)


st.title('Source IP Analysis')
st.write('Bar chart of Source IP by number of requests')
st.write('Time Range:', start_time, 'to', end_time)
st.altair_chart(bar_chart, use_container_width=True)
