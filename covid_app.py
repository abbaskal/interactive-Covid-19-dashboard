import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime as dt
from urllib.request import urlopen
import json
from warnings import filterwarnings

st.set_page_config(layout="wide", page_title='Covid Dashboards', page_icon="download.png")

filterwarnings('ignore')
plt.style.use('seaborn')

st.sidebar.image('look.jpg')
st.sidebar.title("Visualization Selector")
st.sidebar.write("Feel free to play graphs!")
chart_select = st.sidebar.radio("Navigation Panel", (["Home", "Country Based", "USA"]))
st.cache(persist=True)
if chart_select == "Home":
    ## HOMEPAGE
    padding = 10
    st.markdown(f""" <style>
        .reportview-container .main .block-container{{
            padding-top: {padding}rem;
            padding-right: {padding}rem;
            padding-left: {padding}rem;
            padding-bottom: {padding}rem;
        }} </style> """, unsafe_allow_html=True)
    # setting title
    st.markdown("# Welcome! We are happy that you are using our interactive Covid-19 Dashboard ")

    st.image('covid.jpg')

    st.markdown("This project is performed by the CRI Digital Science Students at Paris/France.  "
                "The dashboard will visualize the Covid-19 Situation in All Countries "
                "Coronavirus disease (COVID-19) is an infectious disease caused by a newly discovered coronavirus. Most people infected with the COVID-19 virus will experience mild to moderate respiratory illness and recover without requiring special treatment."
                "we would like analyze current situation of Covid on the world. ")

    st.markdown(
        "(Our open-source data taken from this link: https://www.kaggle.com/antgoldbloom/covid19-data-from-john-hopkins-university) ")

    dataset = st.beta_container()
    with dataset:
        st.write("Dataset Sample")

        data = pd.read_csv("owid-covid-data.csv")
        st.write(data.head(10))
    st.markdown(
        "This is a snippet of the covid data over a range of locations, in an attempt to reduce redundancy, irrelevant variables have been eliminated")
st.cache(persist=True)
if chart_select == "Country Based":

    st.markdown("# Please choose the countries from the selector below")
    st.markdown(" You can also select the period which you wish to see the data in")
    df = pd.read_csv(
        "owid-covid-data.csv")  # reading the owid-covid-data.csv file reference ===>   "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    country_name_input = st.multiselect(
        'Country name',
        df.groupby('location').count().reset_index()[
            'location'].tolist())  # selecting the name of the country among the countries list

    start_date = st.date_input("Choose the start date", value=dt.strptime("2020-02-24", "%Y-%m-%d"),
                               min_value=dt.strptime("2020-02-24", "%Y-%m-%d"),
                               max_value=dt.strptime("2021-06-08", "%Y-%m-%d"))  # choosing the start date

    end_date = st.date_input("Choose the end date", value=dt.strptime("2021-06-08", "%Y-%m-%d"), min_value=start_date,
                             max_value=dt.strptime("2021-06-08", "%Y-%m-%d"))  # choosing the end date

    if len(country_name_input) > 0:
        subset_data = df[df['location'].isin(country_name_input)]  # getting the stats of the selected country/ies
        subset_data = subset_data.sort_values(by="date")  # sorting values based on the date
        subset_data = subset_data[(subset_data["date"] > str(start_date)) & (
                    subset_data["date"] < str(end_date))]  # filtering data based on the selected period
        variable = st.selectbox("cases | deaths", ["cases", "deaths"])


        def draw_plots(variable):
            st.markdown(f'<h2 style="text-align: center;"> Analyzing and Comparing of the total {variable} caused by COVID-19 </h2>', unsafe_allow_html=True)
            total_graph = px.line(x=subset_data["date"],
                                  y=subset_data[f"total_{variable}"],
                                  width=1000,
                                  color=subset_data["location"],
                                  )  # plotly graph
            total_graph.update_layout(title=f'Comparision of the total {variable} caused by COVID-19',
                                      xaxis=dict(title='Date'),
                                      yaxis=dict(title=f'total {variable}'),
                                      legend_title=dict(text='<b>Countries</b>')
                                      )
            st.plotly_chart(total_graph)  # showing plotly graph

            total_per_million_graph = px.line(x=subset_data["date"],
                                              y=subset_data[f"total_{variable}_per_million"],
                                              width=1000,
                                              color=subset_data["location"],
                                              )  # plotly graph
            total_per_million_graph.update_layout(title=f'Comparision of the total {variable} per million caused by COVID-19',
                                                  xaxis=dict(title='Date'),
                                                  yaxis=dict(title=f'total {variable} per million'),
                                                  legend_title=dict(text='<b>Countries</b>')
                                                  )
            st.plotly_chart(total_per_million_graph)


        draw_plots(variable=variable)  # showing plotly graph
        
st.cache(persist=True)
if chart_select == "USA":
    st.markdown("# Explore the US COVID data on the map")
    cases = pd.read_csv("CONVENIENT_us_confirmed_cases.csv"
                    ,index_col= False
                    ,header = None
                   ).transpose()

    #adding column names to the cases data 
    cases.columns = cases.iloc[0]
    cases = cases.iloc[1:,0:]

    #deaths 
    deaths = pd.read_csv("CONVENIENT_us_deaths.csv"
                        ,index_col= False
                        ,header = None
                    ).transpose()

    #chaning column names to the first row values 
    deaths.columns = deaths.iloc[0]
    deaths = deaths.iloc[1:,0:]

    cases_md = pd.read_csv("CONVENIENT_us_metadata.csv")

    #fips data to get the FIPS id 
    fips = pd.read_csv("RAW_us_confirmed_cases.csv").iloc[:,0:7]

    #filling null with 0s 
    fips.FIPS = fips.FIPS.fillna(0) #replacing NA values with 0


    # appending metadata to original data 
    merged_data = pd.merge(cases_md, cases, on = ('Province_State','Admin2'), how = 'left')

    #appending FIPS data to the metadata + original data - FIPS id needs to be used in the mapping 
    merged_data = pd.merge(fips,merged_data, on = ('Province_State','Admin2'),how = 'left')

    fd = pd.concat(
                    [ merged_data[['Province_State','Admin2','Population','FIPS','Lat','Long']]
                    ,merged_data.iloc[:,10:].astype(float).sum(axis = 1)] #this code gives the sum     
                    ,axis = 1)

    #chaning the column name from 0 to Total cases 
    fd =  fd.rename(columns = {0:'Total_cases'})

    # changing FIPS column from float to string and appending leading zeros to be in compliance with the FIPS format 
    fd.FIPS = fd.FIPS.astype(int).astype(str).str.zfill(5) 


    from urllib.request import urlopen
    import json

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)


    fig = px.choropleth_mapbox(fd,geojson=counties , locations = 'FIPS', color='Total_cases',
                            color_continuous_scale= "earth", #"Viridis",
                            range_color=(0,4000),
                            mapbox_style= "carto-darkmatter", #"carto-positron","open-street-map",
                            zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                            opacity=0.5,
                            hover_data=["Province_State", "Admin2"],
                            template = 'plotly_dark',
                            #title = 'COVID - 19 Cases Across USA - County View',
                            labels={'Total_cases': 'COVID Cases'},
                            width= 1000
                            )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig)