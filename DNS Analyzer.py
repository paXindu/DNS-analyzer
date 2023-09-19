import streamlit as st



st.set_page_config(page_title='DNS Analyzer', page_icon=':globe_with_meridians:')


st.markdown(
    """
    <h1 style="text-align: center;">Welcome to DNS eye</h1>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div style="text-align: center; padding: 0 20px;">
        DNS eye is a tool that provides analysis and visualization of DNS data.
        Explore various DNS metrics and gain insights into your DNS infrastructure.
        <br/><br/>
        Please select an option from the sidebar to get started.
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown('---')

