import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Web App URL: 
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://i.imgur.com/UbOXYAU.png"
st.sidebar.image(logo)

# Customize page title
st.title("DAC Reporting App")

st.markdown(
    """
Reporting in data analytics is the process of transforming raw data into a clear and concise format that can be easily understood by stakeholders. 
It's about presenting information in a way that highlights key metrics, trends, and insights. 
Think of it as the communication bridge between complex data and actionable decisions.
    """
)

st.header("Instructions")

markdown = """
1. Add a new app to the `pages/` directory with an emoji in the file name, e.g., `1_🚀_Chart.py`.

"""

st.markdown(markdown)


