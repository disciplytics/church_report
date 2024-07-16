# import packages
from snowflake.snowpark.context import get_active_session

#from streamlit_dynamic_filters import DynamicFilters

explaination_str = ''' The Group Analytics report displays attendance trends and group member demographics and locations.

Select one group at a time for optimal performance.

If the map visual does not have bubbles or is collapsed, please expand the map with the button to the top right of the visual.

                '''


# Get current session
session = get_active_session()

import streamlit as st
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(page_title="Group Analytics",layout="wide")
st.title('Group Analytics')

with st.expander("Click to Learn More"):
        st.write(explaination_str)


# load analytical dataframe
group_df = session.table('ANALYTICAL_GROUPS_ATTENDANCE').to_pandas()

group_df['MILES_BETWEEN_GROUP_AND_PERSON'] = np.round(pd.to_numeric(group_df['MILES_BETWEEN_GROUP_PERSON']),2)
group_df.loc[group_df['ATTENDED'] == 'True', 'ATTENDANCES'] = 1
group_df['ATTENDANCES'] = group_df['ATTENDANCES'].fillna(0)

dates = ['STARTS_AT', 'ENDS_AT']
for i in dates:
    group_df[i] = pd.to_datetime(group_df[i])

 # get filters
col1, col2, col3, col4 = st.columns(4)


with col1:
    sel1 = st.multiselect(
            "Select Group Name (Click to see more!)",
            pd.Series(pd.unique(group_df['GROUP_NAME'])).sort_values(),
            pd.Series(pd.unique(group_df['GROUP_NAME'])).sort_values()[:1]
            )
with col2:
    sel2 = st.multiselect(
            "Select Primary Campus",
            pd.Series(pd.unique(group_df['PRIMARY_CAMPUS'])).sort_values(),
            pd.Series(pd.unique(group_df['PRIMARY_CAMPUS'])).sort_values())

with col3:
    sel3 = st.date_input(
        "Select Start Group Date Range",
        value = pd.to_datetime(group_df['STARTS_AT'].min()))
with col4:
    sel4 = st.date_input(
        "Select End Group Date Range",
        value = pd.to_datetime(group_df['ENDS_AT'].max()))


#group_df['STARTS_AT'] = pd.to_datetime(group_df['STARTS_AT']).dt.strftime("%Y-%m-%d")
#group_df['ENDS_AT'] = pd.to_datetime(group_df['ENDS_AT']).dt.strftime("%Y-%m-%d")

df_selection = group_df.query('`GROUP_NAME`== @sel1').query('`PRIMARY_CAMPUS`== @sel2').query('`STARTS_AT`>= @sel3').query('`STARTS_AT`<= @sel4')


tab1, tab2, tab3 = st.tabs(['Attendance Trends', 'Attendee Breakdown', 'Attendee Locations'])
with tab1:
    try:
        st.subheader('Group Attendance Trends')
        trend_fig = st.bar_chart(
            df_selection.groupby(['STARTS_AT', 'MEMBERSHIP'])['ATTENDANCES'].sum().reset_index(),
            x="STARTS_AT",
            y="ATTENDANCES",
            color = 'MEMBERSHIP',)
    except:
        st.write("No data for current selection. Try selecting more data.")

with tab2:
    st.subheader('Attendee Membership and Age Group')
    try:
        st.bar_chart(
                df_selection.groupby(['MEMBERSHIP', 'AGE_GROUP'])['ATTENDANCES'].sum().reset_index(),
                y="ATTENDANCES",
                x="MEMBERSHIP",
                color = 'AGE_GROUP',)
    except:
        st.write("No data for current selection. Try selecting more data.")

    st.subheader('Average Distance (Miles) Between Attendee and Their Group')
    try:
        st.bar_chart(
                df_selection.groupby(['MEMBERSHIP'])['MILES_BETWEEN_GROUP_AND_PERSON'].mean().reset_index(),
                y="MILES_BETWEEN_GROUP_AND_PERSON",
                x="MEMBERSHIP",)
    except:
        st.write("No data for current selection. Try selecting more data.")
       
with tab3:
    group_locs = df_selection[['GROUP_LATITUDE', "GROUP_LONGITUDE"]].rename(columns={'GROUP_LATITUDE':'LATITUDE', "GROUP_LONGITUDE":"LONGITUDE"})

    person_locs = df_selection[['ATTENDANCES', 'PERSON_LATITUDE', "PERSON_LONGITUDE"]].rename(columns={'PERSON_LATITUDE':'LATITUDE', "PERSON_LONGITUDE":"LONGITUDE"})
    person_locs['LONGITUDE'] = pd.to_numeric(person_locs['LONGITUDE'])
    person_locs['LATITUDE'] = pd.to_numeric(person_locs['LATITUDE'])

    person_locs = person_locs.groupby(['LONGITUDE', 'LATITUDE'])['ATTENDANCES'].sum().reset_index()

    
    st.map(person_locs.dropna(), size = 'ATTENDANCES', use_container_width=True)