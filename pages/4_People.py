# import packages
from snowflake.snowpark.context import get_active_session

#from streamlit_dynamic_filters import DynamicFilters

adult_explaination_str = ''' The People Report breaks down the who, what, and where of the people in your database.'''
activity_explaination_str = ''' The "Activity Report" shows activity trends for people in you church. Select different activities to compare and contrast.

Select the date range to query the year(s) you are intereseted. Either use the calendar tool or type in the dates!

The Activity Sequence visual uses the sequence your church has entered in your database.
'''


inactive_explaination_str = ''' The "Inactive Report" shows what types of people have been inactive and why they went inactive.'''
pdq_explaination_str = ''' The "People Data Quality Report" gives three tables of key data points. 

Years Since Last Update: List of active person ids sorted by how many years has passed since the person record has been updated.

Missing Primay Campus: List of active person ids who are not assigned to a campus.

Missing Birthdate: List of active person ids who do not have a recorded birthdate.
'''




# Get current session
session = get_active_session()

import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="People Analytics",layout="wide")
st.title('People Analytics')




# load analytical dataframe
people_data = session.sql('SELECT * FROM ANALYTICAL_PEOPLE').to_pandas()

people_data['LONGITUDE'] = pd.to_numeric(people_data['LONGITUDE'], errors='coerce')
people_data['LATITUDE'] = pd.to_numeric(people_data['LATITUDE'], errors='coerce')


people_tab, activity_tab, inactive_report, quality_tab = st.tabs(["People Report", "Activity Report", "Inactive Report", "People Data Quality Report"])

#adult tab
with people_tab:
    with st.expander("Click to Learn More"):
        st.write(adult_explaination_str)    

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sel1 = st.multiselect(
                "Select Primary Campus",
                people_data['PRIMARY_CAMPUS'].unique(),
                default = people_data['PRIMARY_CAMPUS'].unique())
    with col2:
        sel2 = st.multiselect(
                "Select Age Group",
                people_data['AGE_GROUP'].unique(),
                default = people_data['AGE_GROUP'].unique())
    with col3:
        sel3 = st.multiselect(
                "Select Membership",
                people_data['MEMBERSHIP'].unique(),
                default = people_data['MEMBERSHIP'].unique())
    with col4:
        sel4 = st.multiselect(
                "Select Active Status",
                people_data['STATUS'].unique(),
                default = 'active')
    
    
        
    people_selection = people_data.query('`PRIMARY_CAMPUS`== @sel1').query('`AGE_GROUP`== @sel2').query('`MEMBERSHIP`== @sel3').query('`STATUS`== @sel4')
        

    trend_col, cumu_col, map_col = st.tabs(['Trend View', 'Cumulative View', 'Map View'])
    with trend_col:
        st.write('Newly Created People Trend')
        trend_df = people_selection.groupby(['CREATED_AT', 'PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'New Record Count'})
        # New Record Creation Date
        st.line_chart(
            data = trend_df.groupby(['CREATED_AT'])['New Record Count'].sum().reset_index(),
            x="CREATED_AT",
            y="New Record Count")

    with cumu_col:
        st.write('Newly Created People Cumulative Total')
        cumu_df = people_selection.groupby(['CREATED_AT', 'PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'Total People'})

        cumu_df = cumu_df.groupby(['CREATED_AT'])['Total People'].sum()
        
        cumu_df = cumu_df.cumsum().reset_index()
        # New Record Creation Date
        st.line_chart(
            data = cumu_df,
            x="CREATED_AT",
            y="Total People")

    
    with map_col:
        st.map(people_selection.groupby(['LATITUDE', 'LONGITUDE'])['PERSON_ID'].size().reset_index(), size='PERSON_ID', use_container_width=True)

    counts_tab, tenure_tab, age_tab = st.tabs(['People Counts', 'People Tenure', 'People Age'])
    
    with counts_tab:
        membership_col, age_group_col, marital_status_col = st.columns(3)

        membership_col.write('People By Membership')
        membership_col.bar_chart(
            people_selection.groupby(['MEMBERSHIP'])['PERSON_ID'].size().reset_index().sort_values(by = ['PERSON_ID'], ascending=False).rename(columns={'PERSON_ID': 'People Count'}),
            y="People Count",
            x="MEMBERSHIP",)

        age_group_col.write('People By Age Group')
        age_group_col.bar_chart(
            people_selection.groupby(['AGE_GROUP'])['PERSON_ID'].size().sort_values(ascending=True).reset_index().rename(columns={'PERSON_ID': 'People Count'}),
            y="People Count",
            x="AGE_GROUP",)

        marital_status_col.write('People By Marital Status')
        marital_status_col.bar_chart(
            people_selection.groupby(['MARITAL_STATUS'])['PERSON_ID'].size().sort_values(ascending=True).reset_index().rename(columns={'PERSON_ID': 'People Count'}),
            y="People Count",
            x="MARITAL_STATUS",)

    
    with tenure_tab:
        membership_col_ten, age_group_col_ten, marital_status_col_ten = st.columns(3)
    
        membership_col_ten.write('Avg Tenure By Membership')
        membership_col_ten.bar_chart(
            people_selection.groupby(['MEMBERSHIP'])['TENURE'].mean().reset_index().sort_values(by = ['TENURE'], ascending=False),
            y="TENURE",
            x="MEMBERSHIP",)

        age_group_col_ten.write('Avg Tenure By Age Group')
        age_group_col_ten.bar_chart(
            people_selection.groupby(['AGE_GROUP'])['TENURE'].mean().sort_values(ascending=True).reset_index(),
            y="TENURE",
            x="AGE_GROUP",)

        marital_status_col_ten.write('Avg Tenure By Marital Status')
        marital_status_col_ten.bar_chart(
            people_selection.groupby(['MARITAL_STATUS'])['TENURE'].mean().sort_values(ascending=True).reset_index(),
            y="TENURE",
            x="MARITAL_STATUS",)
    
    with age_tab:
        membership_col_age, marital_status_col_age = st.columns(2)
    
        membership_col_age.write('Avg Age By Membership')
        membership_col_age.bar_chart(
            people_selection.groupby(['MEMBERSHIP'])['AGE'].mean().reset_index().sort_values(by = ['AGE'], ascending=False),
            y="AGE",
            x="MEMBERSHIP",)

        marital_status_col_age.write('Avg Age By Marital Status')
        marital_status_col_age.bar_chart(
            people_selection.groupby(['MARITAL_STATUS'])['AGE'].mean().sort_values(ascending=True).reset_index(),
            y="AGE",
            x="MARITAL_STATUS",)


with activity_tab:
    with st.expander("Click to Learn More"):
        st.write(activity_explaination_str)

    field_data = session.table('PUBLIC.ANALYTICAL_FIELD').to_pandas()

    col11, col12, col13, col14 = st.columns(4)

    with col11:
        sel11 = st.multiselect(
                "Select Primary Campus",
                field_data['PRIMARY_CAMPUS'].unique(),
                default = field_data['PRIMARY_CAMPUS'].unique())
    with col12:
        sel12 = st.multiselect(
                "Select Age Group",
                field_data['AGE_GROUP'].unique(),
                default = field_data['AGE_GROUP'].unique())
    with col13:
        sel13 = st.multiselect(
                "Select Membership",
                field_data['MEMBERSHIP'].unique(),
                default = field_data['MEMBERSHIP'].unique())
    with col14:
        sel14 = st.multiselect(
                "Select Marital Status",
                field_data['MARITAL_STATUS'].unique(),
                default = field_data['MARITAL_STATUS'].unique())

    
        
    people_act_data = field_data.query('`PRIMARY_CAMPUS`== @sel11').query('`AGE_GROUP`== @sel12').query('`MEMBERSHIP`== @sel13').query('`MARITAL_STATUS`== @sel14')
    people_act_data['ACTIVITY_DATE'] = pd.to_datetime(people_act_data['ACTIVITY_DATE'])

    sel15 = st.multiselect(
            "Select Activity Type",
            people_act_data['ACTIVITY_TYPE'].unique(),
            default = people_act_data['ACTIVITY_TYPE'].unique())
    
    people_act_data = people_act_data.query('`ACTIVITY_TYPE`== @sel15')
    
    sel5 = st.multiselect(
            "Select Activity (More In Drop Down!)",
            people_act_data['ACTIVITY'].unique(),
            default = people_act_data['ACTIVITY'].unique()[:5])

    col20, col21 = st.columns(2)
    
    with col20:
        sel20 = st.date_input(
            "Select Start Activity Date Range",
            value = pd.to_datetime(people_act_data['ACTIVITY_DATE'].min()))
    with col21:
        sel21 = st.date_input(
            "Select End Activity Date Range",
            value = pd.to_datetime(people_act_data['ACTIVITY_DATE'].max()))

    
    
    people_act_data = people_act_data.query('`ACTIVITY`== @sel5').query('`ACTIVITY_DATE`>= @sel20').query('`ACTIVITY_DATE`<= @sel21')
    try:
        activity_trend_df = people_act_data.groupby(['PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS', 'ACTIVITY', 'ACTIVITY_DATE'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'People Count'})
        # New activity
        act_fig = px.line(
                            activity_trend_df.groupby(['ACTIVITY', 'ACTIVITY_DATE'])['People Count'].sum().reset_index(),
                            x="ACTIVITY_DATE",
                            y= 'People Count',
                            color = 'ACTIVITY',
                            title = 'Activity Trends',
                            render_mode='svg'
                        ).update_layout(yaxis_title=None, xaxis_title=None)
        st.plotly_chart(act_fig, theme="streamlit",use_container_width=True,height=900)
    except:
        st.write("No data for current selection. Try selecting more data.")

    try:
        activity_seq_df = people_act_data.groupby(['PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS', 'ACTIVITY', 'ACTIVITY_SEQUENCE', 'ACTIVITY_DATE'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'People Count'})
        # New activity
        act_fig = px.bar(
                            activity_seq_df.groupby(['ACTIVITY', 'ACTIVITY_SEQUENCE'])['People Count'].sum().reset_index(),
                            x="ACTIVITY_SEQUENCE",
                            y= 'People Count',
                            color = 'ACTIVITY',
                            title = 'Activity Sequence',
                            barmode='group'
                        ).update_layout(yaxis_title=None, xaxis_title=None)
        st.plotly_chart(act_fig, theme="streamlit",use_container_width=True,height=900)
    except:
        st.write("No data for current selection. Try selecting more data.")



    # activity by demographics

    activity_campus_tab, activity_membership_tab, activity_agegroup_tab, activity_marital_tab = st.tabs(['Activty By Campus', 'Activty By Membership', 'Activty By Age Group', 'Activty Marital Status'])

    try:
        people_act_data_bd = people_act_data.groupby(['PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS', 'ACTIVITY', 'ACTIVITY_DATE'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'People Count'})
    except:
        pass


    with activity_campus_tab:
        try:
            
            act_pc_count_fig = px.bar(
                people_act_data_bd.groupby(['ACTIVITY', 'PRIMARY_CAMPUS'])['People Count'].sum().sort_values().reset_index(),
                y="ACTIVITY",
                x="People Count",
                color="PRIMARY_CAMPUS", 
                barmode="group",
                title = 'Activity Participants By Primary Campus').update_layout(yaxis_title=None, xaxis_title=None)
            activity_campus_tab.plotly_chart(act_pc_count_fig, theme="streamlit", use_container_width=True)
        except:
            pass


    with activity_membership_tab:
        try:
            act_pc_count_fig = px.bar(
                people_act_data_bd.groupby(['ACTIVITY', 'MEMBERSHIP'])['People Count'].sum().sort_values().reset_index(),
                y="ACTIVITY",
                x="People Count",
                color="MEMBERSHIP", 
                barmode="group",
                title = 'Activity Participants By Membership').update_layout(yaxis_title=None, xaxis_title=None)
            activity_membership_tab.plotly_chart(act_pc_count_fig, theme="streamlit", use_container_width=True)
        except:
            pass

    with activity_agegroup_tab:
        try:
            act_pc_count_fig = px.bar(
                people_act_data_bd.groupby(['ACTIVITY', 'AGE_GROUP'])['People Count'].sum().sort_values().reset_index(),
                y="ACTIVITY",
                x="People Count",
                color="AGE_GROUP", 
                barmode="group",
                title = 'Activity Participants By Age Group').update_layout(yaxis_title=None, xaxis_title=None)
            activity_agegroup_tab.plotly_chart(act_pc_count_fig, theme="streamlit", use_container_width=True)
        except:
            pass

    with activity_marital_tab:
        try:
            act_pc_count_fig = px.bar(
                people_act_data_bd.groupby(['ACTIVITY', 'MARITAL_STATUS'])['People Count'].sum().sort_values().reset_index(),
                y="ACTIVITY",
                x="People Count",
                color="MARITAL_STATUS", 
                barmode="group",
                title = 'Activity Participants By Marital Status').update_layout(yaxis_title=None, xaxis_title=None)
            activity_marital_tab.plotly_chart(act_pc_count_fig, theme="streamlit", use_container_width=True)
        except:
            pass


with inactive_report:
    with st.expander("Click to Learn More"):
        st.write(inactive_explaination_str)
        
    inactive_data = people_data[(people_data['STATUS'] == 'inactive')]


    col6, col7, col8, col9 = st.columns(4)

    with col6:
        sel6 = st.multiselect(
                "Campus",
                inactive_data['PRIMARY_CAMPUS'].unique(),
                default = inactive_data['PRIMARY_CAMPUS'].unique())
    with col7:
        sel7= st.multiselect(
                "Age Group",
                inactive_data['AGE_GROUP'].unique(),
                default = inactive_data['AGE_GROUP'].unique())
    with col8:
        sel8 = st.multiselect(
                "Membership",
                inactive_data['MEMBERSHIP'].unique(),
                default = inactive_data['MEMBERSHIP'].unique())
    with col9:
        sel9 = st.multiselect(
                "Marital Status",
                inactive_data['MARITAL_STATUS'].unique(),
                default = inactive_data['MARITAL_STATUS'].unique())

    
    

    inactive_selection = inactive_data.query('`PRIMARY_CAMPUS`== @sel6').query('`AGE_GROUP`== @sel7').query('`MEMBERSHIP`== @sel8').query('`MARITAL_STATUS`== @sel9')
    
    try:
        inactive_trend_df = inactive_selection.groupby(['INACTIVATED_AT', 'PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'Inactive Count'})
        # New Inactive Date
        inactive_trend_fig = px.line(
                            inactive_trend_df.groupby(['INACTIVATED_AT'])['Inactive Count'].sum().reset_index(),
                            x="INACTIVATED_AT",
                            y="Inactive Count",
                            title = 'Inactive People Trend',
                            render_mode='svg'
                        ).update_layout(yaxis_title=None, xaxis_title=None)
        st.plotly_chart(inactive_trend_fig, theme="streamlit", use_container_width=True)
    except:
        st.write("No data for current selection. Try selecting more data.")

    inactive_reason_tab, inactive_campus_tab, inactive_membership_tab, inactive_age_group_tab = st.tabs(['Inactive Reasons', 'Campus View', 'Membership View', 'Age Group View'])

    with inactive_reason_tab:
        try:
            reason_df = inactive_selection.groupby(['INACTIVE_REASON', 'PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'Inactive Count'})
            reason_count_fig = px.bar(
                reason_df.groupby(['INACTIVE_REASON'])['Inactive Count'].sum().reset_index(),
                x="INACTIVE_REASON",
                y="Inactive Count",
                title = 'People By Inactive Reason').update_layout(yaxis_title=None, xaxis_title=None)
        except:
            pass
        
        try:
            inactive_reason_tab.plotly_chart(reason_count_fig, theme="streamlit", use_container_width=True)
        except:
            inactive_reason_tab.write("No data for current selection. Try selecting more data.")

    with inactive_campus_tab:
        try:
            campus_reason_df = inactive_selection.groupby(['INACTIVE_REASON', 'PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'Inactive Count'})
            campus_reason_fig = px.bar(
                campus_reason_df.groupby(['INACTIVE_REASON', 'PRIMARY_CAMPUS'])['Inactive Count'].sum().reset_index(),
                x="Inactive Count",
                y="PRIMARY_CAMPUS",
                color="INACTIVE_REASON", 
                barmode="group",
                title = 'Inactive People By Campus').update_layout(yaxis_title=None, xaxis_title=None)
        except:
            pass
        
        try:
            inactive_campus_tab.plotly_chart(campus_reason_fig, theme="streamlit", use_container_width=True)
        except:
            inactive_campus_tab.write("No data for current selection. Try selecting more data.")

    with inactive_membership_tab:
        try:
            mem_reason_df = inactive_selection.groupby(['INACTIVE_REASON', 'PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'Inactive Count'})
            mem_reason_fig = px.bar(
                mem_reason_df.groupby(['INACTIVE_REASON', 'MEMBERSHIP'])['Inactive Count'].sum().reset_index(),
                x="Inactive Count",
                y="MEMBERSHIP",
                color="INACTIVE_REASON", 
                barmode="group",
                title = 'Inactive People By Membership').update_layout(yaxis_title=None, xaxis_title=None)
        except:
            pass
        
        try:
            inactive_membership_tab.plotly_chart(mem_reason_fig, theme="streamlit", use_container_width=True)
        except:
            inactive_membership_tab.write("No data for current selection. Try selecting more data.")

    with inactive_age_group_tab:
        try:
            ag_reason_df = inactive_selection.groupby(['INACTIVE_REASON', 'PRIMARY_CAMPUS', 'AGE_GROUP', 'MEMBERSHIP', 'MARITAL_STATUS'])['PERSON_ID'].size().reset_index().rename(columns={'PERSON_ID': 'Inactive Count'})
            ag_reason_fig = px.bar(
                ag_reason_df.groupby(['INACTIVE_REASON', 'AGE_GROUP'])['Inactive Count'].sum().reset_index(),
                x="Inactive Count",
                y="AGE_GROUP",
                color="INACTIVE_REASON", 
                barmode="group",
                title = 'Inactive People By Age Group').update_layout(yaxis_title=None, xaxis_title=None)
        except:
            pass
        
        try:
            inactive_age_group_tab.plotly_chart(ag_reason_fig, theme="streamlit", use_container_width=True)
        except:
            inactive_age_group_tab.write("No data for current selection. Try selecting more data.")

with quality_tab:
    with st.expander("Click to Learn More"):
        st.write(pdq_explaination_str)
        
    quality_selection = people_data[(people_data['STATUS'] == 'active')]
    
    yrs_update_col, missing_campus_col, missing_birthdate_col = st.columns(3)
    
    with yrs_update_col:
        st.subheader("Years Since Last Update")
        st.dataframe(quality_selection.sort_values(by=['YEARS_SINCE_UPDATE'], ascending = False)[['PERSON_ID', 'YEARS_SINCE_UPDATE']].reset_index(drop=True))

    with missing_campus_col:
        st.subheader("Missing Primary Campus")
        st.dataframe(quality_selection[quality_selection['PRIMARY_CAMPUS'] == 'Unknown'].sort_values(by=['YEARS_SINCE_UPDATE'], ascending = False)[['PERSON_ID', 'PRIMARY_CAMPUS', 'YEARS_SINCE_UPDATE']].reset_index(drop=True))


    with missing_birthdate_col:
        st.subheader("Missing Birthdate")
        st.dataframe(quality_selection[quality_selection['AGE'].isna() == True].sort_values(by=['YEARS_SINCE_UPDATE'], ascending = False).rename(columns={'AGE':'BIRTH DATE'})[['PERSON_ID', 'BIRTH DATE', 'YEARS_SINCE_UPDATE']].fillna('Unknown').reset_index(drop=True))
