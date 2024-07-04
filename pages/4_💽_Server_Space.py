import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import altair as alt
import mysql.connector
import plotly.express as px

st.set_page_config(layout="wide")

markdown = """
Web App URL: 
"""

st.sidebar.title("About")
st.sidebar.info(markdown)

st.title("Track Server Usage Stats")

alt.themes.enable("dark")


def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="ohdl_test"
    )

connection = create_connection()
if connection.is_connected():
    st.success("Connected to the database")

def fetch_db_stats(connection):
    try:
        cursor = connection.cursor()
        query = """
             SELECT
                table_schema as DB_name,
                ROUND(SUM(data_length + index_length) / 1024 / 1024 , 0) as size_mb
                FROM
                information_schema.tables
                GROUP BY
                table_schema
                order by 2 desc limit 10;
                """
        cursor.execute(query)
        records = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        df = pd.DataFrame(records, columns=column_names)
        return df
    except mysql.connector.Error as error:
        st.error(f"Failed to fetch visit data from MySQL table: {error}")

#######################
# Load data
        
df_db_stats = fetch_db_stats(connection)
db_columns = ["DB_name","size_mb"]
db_stats_df = pd.DataFrame(df_db_stats, columns = db_columns)


#######################
# Dashboard Main Panel
col = st.columns((2.5, 2.5, 2), gap='medium')
   

with col[1]:
    st.markdown('#### Top 10 Databases')

    db_stats_df["size_mb"] = db_stats_df["size_mb"].astype(float)

    st.dataframe(db_stats_df,
                 column_order=("DB_name", "size_mb"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "DB_name": st.column_config.TextColumn(
                        "Database Name",
                    ),
                    "size_mb": st.column_config.NumberColumn(
                        "Size in MB",
                        format="%d",
                        min_value=0,
                        max_value=max(db_stats_df.size_mb),
                        step=1,
                     )}
                 )
    

