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

st.title("Track Client Visits")

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

def fetch_visits(connection):
    try:
        cursor = connection.cursor()
        query = """
                select 
                    sml.facility,
                    e.site_id ,
                    e.program_id ,
                    extract(month from e.date_created) Month_Date_Created,
                    extract(year from e.date_created) Year_Date_Created,
                    voided,
                    count(*) Records
                    from encounter e 
                    inner join analytics.sites_master_list sml on e.site_id = sml.sites_site_id
                    group by sml.facility,
                    e.site_id ,e.program_id ,extract(month from e.date_created),extract(year from e.date_created),voided;
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
        
df_visits = fetch_visits(connection)
visits_columns = ["facility","site_id","program_id","Month_Date_Created","Year_Date_Created","voided","Records"]
visits_df = pd.DataFrame(df_visits, columns = visits_columns)


#######################

year_list = list(visits_df.Year_Date_Created.unique())[::-1]

selected_year = st.selectbox('Select a year', year_list)
df_selected_year = visits_df[visits_df.Year_Date_Created == selected_year]
df_selected_year_sorted = df_selected_year.sort_values(by="Year_Date_Created", ascending=False)

color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
# selected_color_theme = st.selectbox('Select a color theme', color_theme_list)
selected_color_theme = color_theme_list[2]


#######################
# Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap


def make_bar_chart(df, year_date_created, facility, records, color_theme):
    # df['Year'] = year_date_created['Year_Date_Created']
    df_grouped = df.groupby([year_date_created, facility])[records].sum().reset_index(name='Total')
    
    bar_chart = alt.Chart(df_grouped).mark_bar().encode(
        x=alt.X('Year_Date_Created:O', axis=alt.Axis(title="Year")),
        y=alt.Y('Total:Q', axis=alt.Axis(title="Total Visits (Voided + Unvoided)")),
        color=alt.Color(f'{facility}:N', legend=alt.Legend(title="Facility"), scale=alt.Scale(scheme=color_theme)),
        tooltip=['Year_Date_Created', 'Total', facility]
    ).properties(
        width=800,
        height=400
    )
    return bar_chart

# Convert records to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Calculation of voided and unvoided records
def calculate_voided_unvoided(input_df, input_year):
  selected_year_data = input_df[input_df['Year_Date_Created'] == input_year].reset_index()
  grouped_df = selected_year_data.groupby(['facility','voided'])['Records'].sum().reset_index()
  return grouped_df


#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Voided/Unvoided')

    df_records_difference_sorted = calculate_voided_unvoided(visits_df, selected_year)

    if selected_year > 2010:
        voided_records = 'Voided Records'
        df_filtered = df_records_difference_sorted[df_records_difference_sorted['voided'] == 1]
        sum_records = df_filtered['Records'].sum()
        total_voided_records = format_number(sum_records)
    else:
        voided_records = '-'
        total_voided_records = '-'
    st.metric(label=voided_records, value=total_voided_records)

    if selected_year > 2010:
        un_voided_records = 'Unvoided Records'
        df_filtered_unvoided = df_records_difference_sorted[df_records_difference_sorted['voided'] == 0]
        sum_records = df_filtered_unvoided['Records'].sum()
        total_unvoided_records = format_number(sum_records) 
    else:
        un_voided_records = '-'
        last_state_population = '-'
    st.metric(label=un_voided_records, value=total_unvoided_records)

    
    st.markdown('#### Visits Categorisation')




with col[1]:
    st.markdown('#### Total Visits Per Site')
    
    heatmap = make_heatmap(visits_df, 'Year_Date_Created', 'facility', 'Records', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

    st.markdown('#### Total Visits Trend Analysis')
    bargraph = make_bar_chart(visits_df, 'Year_Date_Created', 'facility','Records',  selected_color_theme)
    st.altair_chart(bargraph, use_container_width=True)
    

with col[2]:
    st.markdown('#### Top Facilities')

    st.dataframe(df_records_difference_sorted,
                 column_order=("facility", "Records"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "facility": st.column_config.TextColumn(
                        "Facility",
                    ),
                    "Records": st.column_config.ProgressColumn(
                        "Records",
                        format="%f",
                        min_value=0,
                        max_value=max(df_records_difference_sorted.Records),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: Central Repository Dataset (CDR).
            - :orange[**Voided/Unvoided**]: Total voided or unvoided records per facility for selected year
            - :orange[**Visits categorisation**]: percentage of facilities with visits > 50,000 per year.
            ''')
