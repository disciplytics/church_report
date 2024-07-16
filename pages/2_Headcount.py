# import packages
from snowflake.snowpark.context import get_active_session

#from streamlit_dynamic_filters import DynamicFilters

explaination_str = ''' The "Headcount Analytics Report" is a simple trend analysis of headcounts over time.

Before getting started, select an Event Name to review the headcounts of interest.

Below the line chart, there is a table breakdown of the trend to understand headcounts by all available features.

                '''


# Get current session
session = get_active_session()

import streamlit as st
import pandas as pd
from datetime import timedelta

# Set page config
st.set_page_config(page_title="Headcount Analytics",layout="wide")
st.title('Headcount Analytics')

with st.expander("Click to Learn More"):
        st.write(explaination_str)


# load analytical dataframe
headcount_df = session.sql('SELECT *, YEAR(TRY_TO_DATE(STARTS_AT)) as YEAR , WEEK(TRY_TO_DATE(STARTS_AT)) as WEEK FROM ANALYTICAL_CHECKINS').to_pandas()

headcount_df['STARTS_AT'] = pd.to_datetime(headcount_df['STARTS_AT']).dt.strftime("%Y-%m-%d")

headcount_df['STARTS_AT'] = pd.to_datetime(headcount_df['STARTS_AT'])

headcount_df['DATE'] = pd.to_datetime(headcount_df['STARTS_AT'])

headcount_df['EVENT_TIME'] = headcount_df['EVENT_TIME'].astype(str)

headcount_df['YEAR'] = headcount_df['YEAR'].astype(str)


headcount_df['TOTAL_ATTENDEES'] = pd.to_numeric(headcount_df['TOTAL_ATTENDEES'])
headcount_df['REGULAR_COUNT'] = pd.to_numeric(headcount_df['REGULAR_COUNT'])
headcount_df['GUEST_COUNT'] = pd.to_numeric(headcount_df['GUEST_COUNT'])
headcount_df['VOLUNTEER_COUNT'] = pd.to_numeric(headcount_df['VOLUNTEER_COUNT'])

 # get filters
col1, col2, col5, col6 = st.columns(4)


with col1:
    sel1 = st.multiselect(
            "Select Event Name",
            pd.Series(pd.unique(headcount_df['EVENT_NAME'])).sort_values(),
            pd.Series(pd.unique(headcount_df['EVENT_NAME'])).head(1),)
with col2:
    sel2 = st.multiselect(
            "Select Attendance Type",
            pd.Series(pd.unique(headcount_df['ATTENDANCE_TYPE'])).sort_values(),
            pd.Series(pd.unique(headcount_df['ATTENDANCE_TYPE'])).sort_values(),)
with col5:
    sel5 = st.date_input(
        "Select Start Event Date Range",
        value = headcount_df['STARTS_AT'].max() - timedelta(days=365*2))
with col6:
    sel6 = st.date_input(
        "Select End Event Date Range",
        value = headcount_df['STARTS_AT'].max())






df_selection = headcount_df.query('`EVENT_NAME`== @sel1').query('`ATTENDANCE_TYPE`== @sel2').query('`STARTS_AT`>= @sel5').query('`STARTS_AT`<= @sel6')


trend_tab, yoy_tab = st.tabs(['Trend View', 'Year/Year View'])

with trend_tab:

    total_report, reg_report, guest_report, vol_report = st.tabs(['Total Headcount Report', 'Regular Headcount Report', 'Guest Headcount Report', 'Volunteer Headcount Report'])
    
    with total_report:
    
        if len(sel1) > 1:
    
            col_trend, col_event, col_time = st.columns(3)
            
            try:
                st.subheader('Total Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['DATE'])['TOTAL_ATTENDEES'].sum().reset_index(),
                    x="DATE",
                    y="TOTAL_ATTENDEES")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
            
            try:
                st.subheader('Total Headcount By Event')
                event_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_NAME'])['TOTAL_ATTENDEES'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="TOTAL_ATTENDEES",
                    color='EVENT_NAME')
            except:
                col_event.write("No data for current selection. Try selecting more data.")
        
            try:
                st.subheader('Total Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_TIME'])['TOTAL_ATTENDEES'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="TOTAL_ATTENDEES",
                    color='EVENT_TIME')
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
        else:
    
            col_trend, col_time = st.columns(2)
            
            try:
                st.subheader('Total Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['DATE'])['TOTAL_ATTENDEES'].sum().reset_index(),
                    x="DATE",
                    y="TOTAL_ATTENDEES")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
        
            try:
                st.subheader('Total Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_TIME'])['TOTAL_ATTENDEES'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="TOTAL_ATTENDEES",
                    color='EVENT_TIME')
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
    with reg_report:
    
        if len(sel1) > 1:
    
            col_trend, col_event, col_time = st.columns(3)
            
            try:
                st.subheader('Regular Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['DATE'])['REGULAR_COUNT'].sum().reset_index(),
                    x="DATE",
                    y="REGULAR_COUNT")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
            
            try:
                st.subheader('Regular Headcount By Event')
                event_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_NAME'])['REGULAR_COUNT'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="REGULAR_COUNT",
                    color='EVENT_NAME')
            except:
                col_event.write("No data for current selection. Try selecting more data.")
        
            try:
                st.subheader('Regular Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_TIME'])['REGULAR_COUNT'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="REGULAR_COUNT",
                    color='EVENT_TIME')
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
        else:
    
            col_trend, col_time = st.columns(2)
            
            try:
                st.subheader('Regular Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['DATE'])['REGULAR_COUNT'].sum().reset_index(),
                    x="DATE",
                    y="REGULAR_COUNT")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
        
            try:
                st.subheader('Regular Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_TIME'])['REGULAR_COUNT'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="REGULAR_COUNT",
                    color='EVENT_TIME')
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
    with guest_report:
    
        if len(sel1) > 1:
    
            col_trend, col_event, col_time = st.columns(3)
            
            try:
                st.subheader('Guest Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['DATE'])['GUEST_COUNT'].sum().reset_index(),
                    x="DATE",
                    y="GUEST_COUNT",)
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
            
            try:
                st.subheader('Guest Headcount By Event')
                event_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_NAME'])['GUEST_COUNT'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="GUEST_COUNT",
                    color='EVENT_NAME')
            except:
                col_event.write("No data for current selection. Try selecting more data.")
        
            try:
                st.subheader('Guest Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_TIME'])['GUEST_COUNT'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="GUEST_COUNT",
                    color='EVENT_TIME',)
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
        else:
    
            col_trend, col_time = st.columns(2)
    
            try:
                st.subheader('Guest Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['DATE'])['GUEST_COUNT'].sum().reset_index(),
                    x="DATE",
                    y="GUEST_COUNT",)
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
        
            try:
                st.subheader('Guest Headcount By Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_TIME'])['GUEST_COUNT'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="GUEST_COUNT",
                    color='EVENT_TIME',)
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
    with vol_report:
    
        if len(sel1) > 1:
    
            col_trend, col_event, col_time = st.columns(3)
            
            try:
                st.subheader('Volunteer Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['DATE'])['VOLUNTEER_COUNT'].sum().reset_index(),
                    x="DATE",
                    y="VOLUNTEER_COUNT")
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
            
            try:
                st.subheader('Volunteer Headcount By Event')
                event_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_NAME'])['VOLUNTEER_COUNT'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="VOLUNTEER_COUNT",
                    color='EVENT_NAME')
            except:
                col_event.write("No data for current selection. Try selecting more data.")
        
            try:
                st.subheader('Volunteer Headcount Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_TIME'])['VOLUNTEER_COUNT'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="VOLUNTEER_COUNT",
                    color='EVENT_TIME',)
            except:
                col_time.write("No data for current selection. Try selecting more data.")
    
        else:
    
            col_trend, col_time = st.columns(2)
            
            try:
                st.subheader('Volunteer Headcount Trends')
                trend_fig = st.bar_chart(
                    df_selection.groupby(['DATE'])['VOLUNTEER_COUNT'].sum().reset_index(),
                    x="DATE",
                    y="VOLUNTEER_COUNT",)
            except:
                col_trend.write("No data for current selection. Try selecting more data.")
        
        
        
            try:
                st.subheader('Volunteer Headcount Event Time')
                time_fig = st.bar_chart(
                    df_selection.groupby(['DATE', 'EVENT_TIME'])['VOLUNTEER_COUNT'].sum().reset_index(),
                    #df_selection,
                    x="DATE",
                    y="VOLUNTEER_COUNT",
                    color='EVENT_TIME',)
            except:
                col_time.write("No data for current selection. Try selecting more data.")



with yoy_tab:

    st.subheader('Total Headcount Year/Year')
    st.bar_chart(
        df_selection.groupby(['YEAR', 'WEEK'])['TOTAL_ATTENDEES'].sum().reset_index(),
        x="WEEK", y="TOTAL_ATTENDEES", color='YEAR')

    st.subheader('Regular Headcount Year/Year')
    st.bar_chart(
        df_selection.groupby(['YEAR', 'WEEK'])['REGULAR_COUNT'].sum().reset_index(),
        x="WEEK", y="REGULAR_COUNT", color='YEAR')

    st.subheader('Guest Headcount Year/Year')
    st.bar_chart(
        df_selection.groupby(['YEAR', 'WEEK'])['GUEST_COUNT'].sum().reset_index(),
        x="WEEK", y="GUEST_COUNT", color='YEAR')

    st.subheader('Volunteer Headcount Year/Year')
    st.bar_chart(
        df_selection.groupby(['YEAR', 'WEEK'])['VOLUNTEER_COUNT'].sum().reset_index(),
        x="WEEK", y="VOLUNTEER_COUNT", color='YEAR')


st.subheader('Table View')
st.write(df_selection)
