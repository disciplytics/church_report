import streamlit as st

#st.set_page_config(
#    page_title="Hello",
#    page_icon="👋",
    
#)

st.write("# Church Analytics")
st.sidebar.success("Select a view above.")

st.markdown(
        """
        **👈 Select a view in the sidebar on the left** to begin diving into your data.
        """)

st.markdown(
        """
        ### App Overview:
        
        ##### App Structure
        
        1. Views: A level of the app that holds reports based on a CMS (Church Management System).
        
        2. Reports: Analytical findings regarding key areas of concern for churhes.
        
        3. Filters: A way to slice and query your data to find patterns or isolate cohorts.
        
        4. Click To Learn More Buttons: In-app documentation to give further context to views and reports.
        
        ##### Analytical Metrics
        
        1. Year-to-Date (YTD): The sum of data in the current year.
        
        2. Year-Over-Year: The difference between the sum of the latest, selected year divided by the sum of the select, previous year.
        
        3. Averages: These can be means or medians. Means are skewed by outliers and median is not. We often use mean to capture outliers.
        
        4. Tenure: The difference between a persons created date and the current date.
        
        ##### Having Issues?
        
        1. App not responding or grayed out? Refresh your browser! Sometimes the server needs a reboot! (We all get tired).
        
        2. Get error messages after filtering? Depending on how much time you have fitlered, some attributes do not show up in a time frame. Try selecting more data through expanding the time range or by adding attributes. 
        
        3. Just stuck? Reach out!
        
        
        ##### More Information:
        
        Disciplytics provides analytics as a service to churches. 
        
        - Check out [Disciplytics](https://disciplytics.com)!

    """
    )