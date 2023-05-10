"""
Name: Preston Webb
CS230: Section 4
Data: Stadiums
URL:

"""

import os
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
from pydeck import data_utils as pdkv


# gets csv data, renames div to division for readability
def getData():
    pat = os.path.join('data', 'stadiums-geocoded.csv')
    df = pd.read_csv(pat).rename(columns={'div': 'division'})
    return df


# uses numpy to get list of states, then uses numpy to get a unique states list
def getStates(df):
    stateList = np.array(df.state.values.tolist())
    stateList = np.unique(stateList)
    return stateList


# uses numpy to get list of conferences, then uses numpy to get a unique conferences list
# adds in an 'all' option for selection
def getConferences(df):
    confList = np.array(df.conference.values.tolist())
    confList = np.unique(confList)
    confList = np.insert(confList, 0, 'All')
    return confList


# uses numpy to get list of stadiums, then uses numpy to get a unique stadium list
def getStadiums(df):
    stadList = np.array(df.stadium.values.tolist())
    stadList = np.unique(stadList)
    return stadList


def Years(df):
    # makes basis of plot, makes bins/ticks for years represented in data
    fig, ax = plt.subplots()
    yearBins = np.arange(1890, step=10, stop=2020)
    # labels, makes histogram and plots it
    plt.title('Histogram of Stadiums\' Years Built')
    plt.hist(df.built, edgecolor='black', bins=yearBins)
    plt.xlabel('Year Built')
    plt.ylabel('Number of Stadiums')
    plt.xticks(yearBins, rotation=45)
    st.pyplot(fig)


# gives user choice of division and then conference, passes chosen data into Map function
def MapPage(df, divOpt):
    if divOpt != 'All':
        df = df.loc[df.division == divOpt]
        # df.loc
        # df.iloc
        confOpt = st.selectbox('Conference Options', getConferences(df))
        if confOpt != 'All':
            df = df.loc[df.conference == confOpt]
    stateOpt = st.multiselect('State Options', getStates(df))
    if len(stateOpt) != 0:
        df = df.loc[df.state.isin(stateOpt)]

    st.write(df)

    Map(df)


# takes passed in data, sorted out select columns
def Map(df):
    mapping = df.filter(['team', 'stadium', 'latitude', 'longitude'])
    # uses built in pydeck function to calculate initial view of map, makes layer, makes tooltip hover popup
    mapView = pdkv.viewport_helpers.compute_view(mapping[['longitude', 'latitude']])
    mapInfo = pdk.Layer('ScatterplotLayer', mapping, get_position='[longitude, latitude]', get_color=[255, 0, 0],
                        radius_min_pixels=3, pickable=True)
    mapTool = {'html': 'Team: {team}</br>Stadium: {stadium}'}
    # compiles layers, view, and tooltip into group and plots them
    mapDeck = pdk.Deck(layers=[mapInfo], tooltip=mapTool, initial_view_state=mapView)
    st.pydeck_chart(mapDeck)


# select conferences, get chosen data, plots and compares data
def ConferenceComparison(df):
    confs = getConferences(df)
    confOpts = st.multiselect("Select Conferences to Compare", confs)
    confData = {}
    # gets data for each conference, puts in dict
    for conf in confOpts:
        confDf = df.loc[df.conference == conf]
        confLen = len(confDf)
        maxSize = confDf.loc[confDf.capacity.idxmax()]
        aveCap = confDf.capacity.mean().round(0)

        confData[conf] = {'Number of Teams': confLen, 'Average Capacity': aveCap, 'Largest Stadium': maxSize.stadium,
                          'Largest Stadium\'s Capacity': maxSize.capacity}
    # turns dict into df, and plots data
    confDf = pd.DataFrame(confData)
    st.table(confDf)
    if len(confOpts) >= 2:
        graphDf = confDf.swapaxes('index', 'columns')
        fig, ax = plt.subplots()
        plt.bar(graphDf.index, graphDf['Average Capacity'], edgecolor='black')
        plt.title('Average Capacity of Selected Conferences')
        plt.xlabel('Conference')
        plt.ylabel('Capacity')
        st.pyplot(fig)


# gets selected stadium data, maps data, and makes comparison data
def StadiumComparison(df):
    confs = getConferences(df)
    confOpt = st.selectbox('Select a Conference to Look At', confs)
    if confOpt != 'All':
        df = df.loc[df.conference == confOpt]
    stads = getStadiums(df)
    stadOpts = st.multiselect('Select Which Stadiums to Compare', stads)
    if len(stadOpts) >= 2:
        df = df.loc[df.stadium.isin(stadOpts)]
        Map(df)
        st.table(df[['stadium', 'city', 'state', 'team', 'conference', 'capacity', 'built', 'expanded', 'division']])


def main():
    df = getData()
    st.title('Stadium Streamlit')
    st.subheader('Preston Webb - CS230')

    # uses radio selction and if/else statements to display selected pages
    pageOpts = ('Home', 'Years', 'Map', 'Conference Comparison', 'Stadium Comparison')
    pageOpt = st.sidebar.radio('Page Option', pageOpts)

    if pageOpt == 'Home':
        # homepage stuff
        showDataOpt = st.checkbox("Show Data")
        if showDataOpt is True:
            st.write(df)
    elif pageOpt == 'Years':
        Years(df)
    elif pageOpt == 'Map':
        divOpts = ('All', 'fbs', 'fcs')
        divOpt = st.radio('Select Division', divOpts)
        MapPage(df, divOpt)
    elif pageOpt == 'Conference Comparison':
        ConferenceComparison(df)
    elif pageOpt == 'Stadium Comparison':
        StadiumComparison(df)


main()