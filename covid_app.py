import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import missingno as msno
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime as dt
from urllib.request import urlopen
import json
from warnings import filterwarnings
filterwarnings('ignore')
plt.style.use('seaborn')


# Upload Data
first_csv = pd.read_csv('12-30-2020.csv',sep=",")
second_csv = pd.read_csv('time_series_covid19_deaths_global.csv',sep=",")
third_csv = pd.read_csv('CONVENIENT_global_confirmed_cases.csv',sep=",")
raw_conf = pd.read_csv('RAW_global_confirmed_cases.csv')
raw_deaths = pd.read_csv('RAW_global_deaths.csv')



confirmed = raw_conf.groupby('Country/Region')[list(raw_conf.columns)[4:]].agg('sum')
death = raw_deaths.groupby('Country/Region')[list(raw_conf.columns)[4:]].agg('sum')


third_csv = third_csv[1:]
third_csv = third_csv.rename(columns={"Country/Region": "Date"}) 





st.title("Covid-19 Dashboard")
st.markdown('The dashboard will visualize the Covid-19 Situation in All Countries')
st.markdown('Coronavirus disease (COVID-19) is an infectious disease caused by a newly discovered coronavirus. Most people infected with the COVID-19 virus will experience mild to moderate respiratory illness and recover without requiring special treatment.')

st.sidebar.title("Visualization Selector")
chart_select= st.sidebar.radio("Analysis Type", (["Country Based"]))

if chart_select == "Overview":
    region = []
    cases = []
    time = []
    latitude = []
    longitude = []
    fat = []
    for u in list(raw_conf.columns)[4:]:
        time.append([u for i in range(raw_conf.shape[0])])
        region.append(list(raw_conf['Country']))
        cases.append(list(raw_conf[u]))
        
        latitude.append(list(raw_conf.Lat))
        longitude.append(list(raw_conf.Long))
        fat.append(list(raw_deaths[u]))
    global_covid19 = pd.DataFrame()
    global_covid19['date'] = np.concatenate(time)
    global_covid19['country'] = np.concatenate(region)
    global_covid19['Lat'] = np.concatenate(latitude)
    global_covid19['Long'] = np.concatenate(longitude)
    global_covid19['cases'] = np.concatenate(cases)
    global_covid19['fatalities'] = np.concatenate(fat)


    center_point = dict(lon=0, lat=0)
    figx = px.density_mapbox(global_covid19, lat='Lat', lon='Long', z="cases",
                            center = center_point, hover_name='country', zoom = 5,
                            range_color= [20, 20] , radius=20,
                            mapbox_style= 'open-street-map', title='Novel Covid19 cases in the world',
                            animation_frame='date',
                            width=1000)
    figx.update(layout_coloraxis_showscale=True)
    st.plotly_chart(figx)

    st.markdown("# Number of Confirmed Cases")
    fig = px.line(third_csv, x="Date", y="Count", color="Country", 
                title='Transition in the number of confirmed cases of each countries',
                template="simple_white", width=1000)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

    st.markdown("# Number of Confirmed Cases in Selected Countries")
    selected_countries  = ["US", "India", "Spain", "Iran", "United Kingdom", "Turkey"]
    df_global_confirmed_cases_selected = third_csv[third_csv["Country"].isin(selected_countries)].reset_index(drop=True)

    fig = px.line(df_global_confirmed_cases_selected, x="Date", y="Count", color="Country", 
              title='Transition in the number of confirmed cases of each countries',
              template="simple_white", width=1000 )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        countries = json.load(response)

if chart_select == "Country Based":
    
    df= pd.read_csv("owid-covid-data.csv") #reading the covid.csv file
    # df["acc_total_deaths"]= df["total_deaths"].cumsum(axis=0) # adds another column for cumulative sum
    country_name_input = st.sidebar.multiselect(
    'Country name',
    df.groupby('location').count().reset_index()['location'].tolist()) #selecting the name of the country among the countries list

    chart_type=st.sidebar.selectbox("Graph Type", ["Line Chart", "Animated Graph"]) #choosing the chart type

    
    if len(country_name_input) > 0:
        subset_data= df[df['location'].isin(country_name_input)] #getting the stats of the selected country/ies
        subset_data= subset_data.sort_values(by="date") #sorting values based on the date

        st.subheader('Comparision of infection growth')
        total_cases_graph= px.line (x= subset_data["date"],
                            y= subset_data["total_deaths"], 
                            width=1000,
                            color=subset_data["location"],
                            ) # plotly graph
        st.plotly_chart(total_cases_graph) #showing plotly graph

if chart_select == "USA":
    def convert_date(date_str):
        return dt.strptime(date_str, '%m/%d/%y')

    third_csv["Date"] = third_csv["Date"].map(convert_date)

    country_cols = [col for col in third_csv.columns if col not in ["Date"]]
    third_csv = pd.melt(third_csv, id_vars=['Date'], value_vars=country_cols,
                                        var_name='Country', value_name='Count')


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
    st.markdown("# Covid Across USA")
    fig = px.choropleth_mapbox(fd,geojson=countries , locations = 'FIPS', color='Total_cases',
                            color_continuous_scale= "earth", #"Viridis",
                            range_color=(0,4000),
                            mapbox_style= "carto-darkmatter", #"carto-positron","open-street-map",
                            zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                            opacity=0.5,
                            hover_data=["Province_State", "Admin2"],
                            template = 'plotly_dark',
                            #title = 'COVID - 19 Cases Across USA - County View',
                            labels={'Total_cases': 'COVID Cases'},
                            width=1000
                            )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)
