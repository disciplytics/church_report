# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import numpy as np
import altair as alt



# Write directly to the app
st.set_page_config(page_title = "Giving Report", layout='wide')
st.title("Giving Report")
st.write(
    """See how giving is trending in your church and who is driving it.
    """
)

# Get the current credentials
session = get_active_session()

# GIVING REPORT
giving_df = session.sql('''
    SELECT 
        CAST(DONATION_YEAR as INT) as YEAR,
        CAST(DONATION_MONTH as INT) as MONTH,
        CAST(DONATION_WEEK as INT) as WEEK,
        CAST(RECEIVED_AT as DATE) as DATE,
        PRIMARY_CAMPUS,
        FUND_NAME,
        MEMBERSHIP,
        AGE_GROUP,
        ZIP,
    	CITY,
    	STATE,
    	CAST(LATITUDE as FLOAT) as LATITUDE,
    	CAST(LONGITUDE as FLOAT) as LONGITUDE,
        STATUS,
        PERSON_ID,
        SUM(DONATION_AMOUNT) as DONATIONS
    FROM ANALYTICAL_GIVING
    GROUP BY ALL
''').to_pandas()


# set default and options, have plan in case church only has one year
try:
    default_giving_years = [giving_df['YEAR'].max(), giving_df['YEAR'].max() - 1]
    option_giving_years = giving_df['YEAR'].unique()

    max_year_week = giving_df[giving_df['YEAR'] == giving_df['YEAR'].max()]['WEEK'].max()
    max_year = giving_df['YEAR'].max()
    
except:
    default_giving_years = [giving_df['YEAR'].max(),]
    option_giving_years = giving_df['YEAR'].unique()

    max_year_week = 52
    max_year = giving_df['YEAR'].max()






giving_tab, forecasts_tab, fee_tab = st.tabs(['Giving Overview', 'Giving Forecasts', 'Giving Fee Report'])


with giving_tab: 


    filter_year_col, filter_pc_col, filter_membership_col, filter_status_col = st.columns([.25, .25, .25, .25])
    with filter_year_col:
        giving_year_sel = st.multiselect(
                'Select Years to Compare',
                options = option_giving_years,
                default = default_giving_years,
            )
    
    with filter_pc_col:
        giving_pc_sel = st.multiselect(
                'Select Primary Campus',
                options = pd.unique(giving_df['PRIMARY_CAMPUS']),
                default = pd.unique(giving_df['PRIMARY_CAMPUS']),
            )
    
    with filter_membership_col:
        giving_mem_sel = st.multiselect(
                'Select Membership',
                options = pd.unique(giving_df['MEMBERSHIP']),
                default = pd.unique(giving_df['MEMBERSHIP']),
            )
    
    with filter_status_col:
        giving_status_sel = st.multiselect(
                'Select Donor Status',
                options = pd.unique(giving_df['STATUS']),
                default = pd.unique(giving_df['STATUS']),
            )

        
    # select data based on year, primary campus
    giving_df_sel = giving_df.query('`YEAR`==@giving_year_sel').query('`PRIMARY_CAMPUS`==@giving_pc_sel').query('`MEMBERSHIP`==@giving_mem_sel').query('`STATUS`==@giving_status_sel').reset_index(drop=True)
    # fix year data type
    giving_df_sel['YEAR'] = giving_df_sel['YEAR'].astype(str)


    # calculate metrics
    most_recent_yr = str(pd.Series(giving_year_sel).max())
    least_recent_yr = str(pd.Series(giving_year_sel).min())
    label_val_ytd = f"YTD Giving - {most_recent_yr}"

    most_recent_ytd = giving_df_sel[giving_df_sel['YEAR'] == most_recent_yr]['DONATIONS'].sum()
    most_recent_avg = giving_df_sel[giving_df_sel['YEAR'] == most_recent_yr]['DONATIONS'].mean()

    label_val_yoy = f"Y/Y Giving - {most_recent_yr}"

    label_val_avg = f"Average Gift - {most_recent_yr}"

    # create reporting params for max year selected
    if most_recent_yr != str(max_year):
        delta_ytd = giving_df_sel[giving_df_sel['YEAR'] == least_recent_yr]['DONATIONS'].sum()

        delta_avg = giving_df_sel[giving_df_sel['YEAR'] == least_recent_yr]['DONATIONS'].mean()
    else:   
        delta_ytd = giving_df_sel[(giving_df_sel['YEAR'] == least_recent_yr) &
                                  (giving_df_sel['WEEK'] <= max_year_week)]['DONATIONS'].sum()

        delta_avg = giving_df_sel[(giving_df_sel['YEAR'] == least_recent_yr) &
                                  (giving_df_sel['WEEK'] <= max_year_week)]['DONATIONS'].mean()


    # trend visuals
    ytd_col, yoy_col, avg_col = st.columns(3)
    
    ytd_col.metric(
        label=label_val_ytd,
        value= '${:,}'.format(np.round(most_recent_ytd,2)),
        delta = f"YTD Giving - {least_recent_yr}: {'${:,}'.format(np.round(delta_ytd,2))}",
        delta_color="off"
    )

    yoy_col.metric(
        label=label_val_yoy,
        value= f"{np.round((most_recent_ytd - delta_ytd)/ delta_ytd * 100,2)}%",
    )

    avg_col.metric(
        label=label_val_avg,
        value= '${:,}'.format(np.round(most_recent_avg,2)),
        delta = f"Avg Gift - {least_recent_yr}: {'${:,}'.format(np.round(delta_avg,2))}",
        delta_color="off"
    )
    
    yoy_w_tab, yoy_m_tab, trend_tab = st.tabs(['Year/Year By Week', 'Year/Year By Month', 'Giving Trend'])
    
    with yoy_w_tab: 
        st.bar_chart(
            data = giving_df_sel.groupby(['YEAR', 'WEEK'])['DONATIONS'].sum().reset_index(),
            x = 'WEEK',
            y = 'DONATIONS',
            color = "YEAR")

    with yoy_m_tab:
        st.bar_chart(
            data = giving_df_sel.groupby(['YEAR', 'MONTH'])['DONATIONS'].sum().reset_index(),
            x = 'MONTH',
           y = 'DONATIONS',
            color = 'YEAR')

    with trend_tab:
        st.bar_chart(
            data = giving_df_sel.groupby(['YEAR', 'DATE'])['DONATIONS'].sum().reset_index(),
            x = 'DATE',
            y = 'DONATIONS'
        )


    st.subheader('Giving Year/Year Breakdowns')
    pc_col, fund_col = st.columns(2)
    
    if pd.Series(giving_year_sel).max() == max_year:
        giving_df_sel = pd.concat([giving_df_sel[(giving_df_sel['YEAR'] == max_year)], giving_df_sel[(giving_df_sel['YEAR'] != max_year) & (giving_df_sel['WEEK'] <=  max_year_week)]]).reset_index(drop=True)
                             
    else:
        pass
    
    yoy_total, yoy_pct = st.tabs(['Y/Y as Total Donations', 'Y/Y As Percent of Total Donations'])
    
    with yoy_total:
        c_pc = alt.Chart(giving_df_sel.groupby(['YEAR', 'PRIMARY_CAMPUS'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).mark_bar().encode(
        x='DONATIONS:Q',
        y=alt.Y('PRIMARY_CAMPUS:N', title=" "),
        color='YEAR:N',
        row=alt.Row("YEAR:N", title=" "),)

        pc_col1, col2 = st.columns([.75, .25])
        pc_col1.write("Primary Campus Breakdown")
        pc_col1.altair_chart(c_pc, use_container_width=True)



        fund_over_col, location_col = st.columns(2)


        top_5_tab, all_tab = st.tabs([f'Top 5 Funds for {most_recent_yr}', 'All Funds'])
    
    
        top_5_funds = giving_df_sel[giving_df_sel['YEAR'] == most_recent_yr].groupby(['FUND_NAME'])['DONATIONS'].sum().sort_values(ascending=False).head(5).index.tolist()

        c_fn_5 = alt.Chart(giving_df_sel.groupby(['YEAR', 'FUND_NAME'])['DONATIONS'].sum().reset_index().query('`FUND_NAME` == @top_5_funds')).mark_bar().encode(
            x='DONATIONS:Q',
            y=alt.Y('FUND_NAME:N', title=" "),
            color='YEAR:N',
            row='YEAR:N')

        fund5_col, col2 = st.columns([.75, .25])
        with fund5_col:
            top_5_tab.write(f'Top 5 Funds for {most_recent_yr} Breakdown')
            top_5_tab.altair_chart(c_fn_5, use_container_width=True)
    
    
        c_fn = alt.Chart(giving_df_sel.groupby(['YEAR', 'FUND_NAME'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).mark_bar().encode(
            x='DONATIONS:Q',
            y=alt.Y('FUND_NAME:N', title=" "),
            color='YEAR:N',
            row='YEAR:N')

        fund_all_col, col2 = st.columns([.75, .25])
        with fund_all_col:
            all_tab.write("All Funds Breakdown")
            all_tab.altair_chart(c_fn, use_container_width=True)

        top_5_tab, all_tab = st.tabs([f'Top 5 Donor Cities for {most_recent_yr}', 'All Donor Cities'])

        top_5_cities = giving_df_sel[giving_df_sel['YEAR'] == most_recent_yr].groupby(['STATE', 'CITY'])['DONATIONS'].sum().sort_values(ascending=False).head(5).reset_index()['CITY'].unique().tolist()

        c_city_5 = alt.Chart(giving_df_sel.groupby(['YEAR', 'STATE', 'CITY'])['DONATIONS'].sum().reset_index().query('`CITY` == @top_5_cities')).mark_bar().encode(
            x='DONATIONS:Q',
            y=alt.Y('CITY:N', title=" "),
            color='YEAR:N',
            row='YEAR:N')

        city5_col, col2 = st.columns([.75, .25])
        with city5_col:
            top_5_tab.write(f'Top 5 Cities for {most_recent_yr} Breakdown')
            top_5_tab.altair_chart(c_city_5, use_container_width=True)
    
    
        c_city = alt.Chart(giving_df_sel.groupby(['YEAR',  'STATE', 'CITY'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).mark_bar().encode(
            x='DONATIONS:Q',
            y=alt.Y('CITY:N', title=" "),
            color='YEAR:N',
            row='YEAR:N')

        city_all_col, col2 = st.columns([.75, .25])
        with city_all_col:
            all_tab.write("All Donor Cities Breakdown")
            all_tab.altair_chart(c_city, use_container_width=True)

        

        c_mem = alt.Chart(giving_df_sel.groupby(['YEAR', 'MEMBERSHIP'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).mark_bar().encode(
        x='DONATIONS:Q',
        y=alt.Y('MEMBERSHIP:N', title=" "),
        color='YEAR:N',
        row='YEAR:N')

        mem_col, col2 = st.columns([.75, .25])
        mem_col.write('Membership Breakdown')
        mem_col.altair_chart(c_mem, use_container_width=True)



        ag_c = alt.Chart(giving_df_sel.groupby(['YEAR', 'AGE_GROUP'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).mark_bar().encode(
        x='DONATIONS:Q',
        y=alt.Y('AGE_GROUP:N', title=" "),
        color='YEAR:N',
        row='YEAR:N')

        ag_col, col2 = st.columns([.75, .25])
        ag_col.write('Age Goup Breakdown')
        ag_col.altair_chart(ag_c, use_container_width=True)


    
        
    with yoy_pct: 
        c_pc = alt.Chart(giving_df_sel.groupby(['YEAR', 'PRIMARY_CAMPUS'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).transform_joinaggregate(
        TotalDonations='sum(DONATIONS)',
            ).transform_calculate(
                PercentOfTotal="datum.DONATIONS / datum.TotalDonations"
            ).mark_bar().encode(
                alt.X('PercentOfTotal:Q', axis=alt.Axis(format='.0%')),
                y=alt.Y('PRIMARY_CAMPUS:N', title=" "),
                color='YEAR:N',
                row=alt.Row("YEAR:N", title=" "),)
        
        pc_col, col2 = st.columns([.75, .25])
        pc_col.write("Primary Campus Breakdown")
        pc_col.altair_chart(c_pc, use_container_width=True)


        top_5_tab, all_tab = st.tabs([f'Top 5 Funds for {most_recent_yr}', 'All Funds'])


        top_5_funds = giving_df_sel[giving_df_sel['YEAR'] == most_recent_yr].groupby(['FUND_NAME'])['DONATIONS'].sum().sort_values(ascending=False).head(5).index.tolist()
    
        c_fn_5 = alt.Chart(giving_df_sel.groupby(['YEAR', 'FUND_NAME'])['DONATIONS'].sum().reset_index().query('`FUND_NAME`==@top_5_funds').reset_index(drop=True)).transform_joinaggregate(
            TotalDonations='sum(DONATIONS)',
                ).transform_calculate(
                    PercentOfTotal="datum.DONATIONS / datum.TotalDonations"
                ).mark_bar().encode(
                    alt.X('PercentOfTotal:Q', axis=alt.Axis(format='.0%')),
                    y=alt.Y('FUND_NAME:N', title=" "),
                    color='YEAR:N',
                    row=alt.Row("YEAR:N", title=" "),)

        fund_5_col, col2 = st.columns([.75, .25])
        with fund_5_col:
            top_5_tab.write(f'Top 5 Funds for {most_recent_yr} Breakdown')
            top_5_tab.altair_chart(c_fn_5, use_container_width=True)
    
    
        c_fn = alt.Chart(giving_df_sel.groupby(['YEAR', 'FUND_NAME'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).transform_joinaggregate(
            TotalDonations='sum(DONATIONS)',
                ).transform_calculate(
                    PercentOfTotal="datum.DONATIONS / datum.TotalDonations"
                ).mark_bar().encode(
                    alt.X('PercentOfTotal:Q', axis=alt.Axis(format='.0%')),
                    y=alt.Y('FUND_NAME:N', title=" "),
                    color='YEAR:N',
                    row=alt.Row("YEAR:N", title=" "),)

        fund_col, col2 = st.columns([.75, .25])
        with fund_col:
            all_tab.write("All Funds Breakdown")
            all_tab.altair_chart(c_fn, use_container_width=True)

        top_5_tab, all_tab = st.tabs([f'Top 5 Donor Cities for {most_recent_yr}', 'All Donor Cities'])
    
        top_5_cities = giving_df_sel[giving_df_sel['YEAR'] == most_recent_yr].groupby(['STATE', 'CITY'])['DONATIONS'].sum().sort_values(ascending=False).head(5).reset_index()['CITY'].unique().tolist()

        c_city_5 = alt.Chart(giving_df_sel.groupby(['YEAR', 'STATE', 'CITY'])['DONATIONS'].sum().reset_index().query('`CITY`==@top_5_cities').reset_index(drop=True)).transform_joinaggregate(
            TotalDonations='sum(DONATIONS)',
                ).transform_calculate(
                    PercentOfTotal="datum.DONATIONS / datum.TotalDonations"
                ).mark_bar().encode(
                    alt.X('PercentOfTotal:Q', axis=alt.Axis(format='.0%')),
                    y=alt.Y('CITY:N', title=" "),
                    color='YEAR:N',
                    row=alt.Row("YEAR:N", title=" "),)

        city_5_col, col2 = st.columns([.75, .25])
        with city_5_col:
            top_5_tab.write(f'Top 5 Cities for {most_recent_yr} Breakdown')
            top_5_tab.altair_chart(c_city_5, use_container_width=True)
    
        
        c_city = alt.Chart(giving_df_sel.groupby(['YEAR',  'STATE', 'CITY'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).transform_joinaggregate(
            TotalDonations='sum(DONATIONS)',
                ).transform_calculate(
                    PercentOfTotal="datum.DONATIONS / datum.TotalDonations"
                ).mark_bar().encode(
                    alt.X('PercentOfTotal:Q', axis=alt.Axis(format='.0%')),
                    y=alt.Y('CITY:N', title=" "),
                    color='YEAR:N',
                    row=alt.Row("YEAR:N", title=" "),)

        all_city_col, col2 = st.columns([.75, .25])
        with all_city_col:
            all_tab.write("All Donor Cities Breakdown")
            all_tab.altair_chart(c_city, use_container_width=True)

        
        c_mem = alt.Chart(giving_df_sel.groupby(['YEAR', 'MEMBERSHIP'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).transform_joinaggregate(
        TotalDonations='sum(DONATIONS)',
            ).transform_calculate(
                PercentOfTotal="datum.DONATIONS / datum.TotalDonations"
            ).mark_bar().encode(
                alt.X('PercentOfTotal:Q', axis=alt.Axis(format='.0%')),
                y=alt.Y('MEMBERSHIP:N', title=" "),
                color='YEAR:N',
                row=alt.Row("YEAR:N", title=" "),)

        mem_col, col2 = st.columns([.75, .25])
        mem_col.write('Membership Breakdown')
        mem_col.altair_chart(c_mem, use_container_width=True)



        
        ag_c = alt.Chart(giving_df_sel.groupby(['YEAR', 'AGE_GROUP'])['DONATIONS'].sum().reset_index().reset_index(drop=True)).transform_joinaggregate(
        TotalDonations='sum(DONATIONS)',
            ).transform_calculate(
                PercentOfTotal="datum.DONATIONS / datum.TotalDonations"
            ).mark_bar().encode(
                alt.X('PercentOfTotal:Q', axis=alt.Axis(format='.0%')),
                y=alt.Y('AGE_GROUP:N', title=" "),
                color='YEAR:N',
                row=alt.Row("YEAR:N", title=" "),)

        ag_col, col2 = st.columns([.75, .25])
        ag_col.write('Age Goup Breakdown')
        ag_col.altair_chart(ag_c, use_container_width=True)

with forecasts_tab:

    fct_explaination_string = '''
    The giving forecast report shows the expected sum of donations for the current year.

    These forecasts are generated by AI models at the primary campus level.

    To ensure your church's forecasts are as accurate as possible, please assign all donors to a campus when appropriate!

    While AI models have shown to be usefule in forecasting, please note that these forecasts are probabalistic and cannot foresee future events that may affect your church's donor patterns. Use this data with care and caution. 
    '''
    with forecasts_tab.expander("Click to Learn More"):
        st.write(fct_explaination_string)

    
    forecasts_df = session.sql(f'''
    SELECT *
    FROM GIVING_FORECASTS_REPORT
    WHERE YEAR(RECEIVED_AT) <= {max_year} 
    AND YEAR(RECEIVED_AT) >= {max_year - 1}
    ''').to_pandas()

    filter_col, col2 = st.columns([.30, .7])

    fct_giving_pc_sel = filter_col.multiselect(
                'Select Forecast By Primary Campus',
                options = pd.unique(forecasts_df['PRIMARY_CAMPUS']),
                default = pd.unique(forecasts_df['PRIMARY_CAMPUS']),
            )
    

    forecasts_df_sel = forecasts_df.query('`PRIMARY_CAMPUS`==@fct_giving_pc_sel')

    
    overview_df = forecasts_df_sel.groupby(['DONATION_YEAR', 'DONATION_MONTH', 'DONATION_WEEK', 'RECEIVED_AT'])[['ACTUAL', 'FORECAST']].sum().reset_index()
    overview_df = pd.melt(overview_df, id_vars=['DONATION_YEAR', 'DONATION_MONTH', 'DONATION_WEEK', 'RECEIVED_AT'], value_vars=['ACTUAL', 'FORECAST'], value_name='DONATIONS', var_name = 'TYPE')

    overview_df['LABEL'] = overview_df['DONATION_YEAR'].astype(str) + " - " + overview_df['TYPE']

    overview_df = overview_df[(overview_df['LABEL'] != f'{max_year-1} - FORECAST')]

    overview_df = overview_df.rename(columns = {'DONATION_YEAR':'YEAR', 'DONATION_MONTH':'MONTH', 'DONATION_WEEK':'WEEK', 'RECEIVED_AT':'DATE'})

    
    # trend visuals
    ytd_col, forecasted_col, yoy_col = st.columns(3)
    
    ytd_col.metric(
        label=f'YTD Giving - {max_year}',
        value= '${:,}'.format(np.round(overview_df[(overview_df['TYPE'] == 'ACTUAL') & (overview_df['YEAR'] == max_year)]['DONATIONS'].sum(),2)),
        delta_color="off"
    )

    forecasted_col.metric(
        label= f'Forecasted Year End Donations - {max_year}',
        value= '${:,}'.format(np.round(overview_df[overview_df.YEAR == max_year].DONATIONS.sum(),2))
    )

    yoy_col.metric(
        label='Forecast Y/Y Growth',
        value= f"{np.round(((overview_df[overview_df.YEAR == max_year].DONATIONS.sum()) - (overview_df[overview_df.YEAR == max_year-1].DONATIONS.sum()))/ (overview_df[overview_df.YEAR == max_year-1].DONATIONS.sum()) * 100,2)}%",
    )

    
    yoy_w_tab, yoy_m_tab, trend_tab = st.tabs(['Forecasted Year/Year By Week', 'Forecasted Year/Year By Month', 'Forecasted Giving Trend'])
    
    with yoy_w_tab: 
        st.bar_chart(
            data = overview_df.groupby(['LABEL', 'WEEK'])['DONATIONS'].sum().reset_index(),
            x = 'WEEK',
            y = 'DONATIONS',
            color = "LABEL")

    with yoy_m_tab:
        st.bar_chart(
            data = overview_df.groupby(['LABEL', 'MONTH'])['DONATIONS'].sum().reset_index(),
            x = 'MONTH',
           y = 'DONATIONS',
            color = 'LABEL')

    with trend_tab:
        st.bar_chart(
            data = overview_df.groupby(['DATE', 'TYPE'])['DONATIONS'].sum().reset_index(),
            x = 'DATE',
            y = 'DONATIONS',
            color='TYPE'
        ) 

with fee_tab:

    fee_analysis = session.sql("""
        SELECT 
            DONATION_YEAR as YEAR, 
            DONATION_MONTH as MONTH,
            PAYMENT_SOURCE, 
            PAYMENT_METHOD, 
            PAYMENT_METHOD_SUB,
            PAYMENT_BRAND,
            FEE_PERCENTAGE,
            FEE_AMOUNT
        FROM ANALYTICAL_GIVING
    """).to_pandas()
    

    fee_explaination_str = ''' 
    
    The "Fee Report" explains what payment funnels are driving the fees.

    The report shows the trend of fees and what payment sources and methods drive the fees. Fees can also be viewed as the total dollar amount or as the average percentage of a gift. 
                            '''

    
    with fee_tab.expander("Click to Learn More"):
        st.write(fee_explaination_str)

    # get filters
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        sel5 = st.multiselect(
            "Select Donation Year",
            pd.Series(pd.unique(fee_analysis['YEAR'])).sort_values(),
            default = [fee_analysis['YEAR'].max(), fee_analysis['YEAR'].max()-1,fee_analysis['YEAR'].max()-2])
    with col6:
        sel6 = st.multiselect(
            "Select Payment Source",
            fee_analysis['PAYMENT_SOURCE'].unique(),
            default = fee_analysis['PAYMENT_SOURCE'].unique())
    with col7:
        sel7 = st.multiselect(
            "Select Payment Method",
            fee_analysis['PAYMENT_METHOD'].unique(),
            default = fee_analysis['PAYMENT_METHOD'].unique())
    with col8:
        sel8 = st.multiselect(
            "Select Payment Method Sub",
            fee_analysis['PAYMENT_METHOD_SUB'].unique(),
            default = fee_analysis['PAYMENT_METHOD_SUB'].unique())

    df_selection_fee = fee_analysis.query('`YEAR`== @sel5').query('`PAYMENT_SOURCE`== @sel6').query('`PAYMENT_METHOD`== @sel7').query('`PAYMENT_METHOD_SUB`== @sel8')
    df_selection_fee['YEAR'] = df_selection_fee['YEAR'].astype(str)
    df_selection_fee['MONTH'] = df_selection_fee['MONTH'].astype(int).round()
    
    st.subheader('Fee Amount Trends')
    fee_trend_fig = st.line_chart(
                        df_selection_fee.groupby(['YEAR', 'MONTH'])['FEE_AMOUNT'].sum().reset_index(),
                        x = 'MONTH',
                        y = 'FEE_AMOUNT',
                        color = 'YEAR')
                    

    fee_amt_tab, fee_pct_tab = st.tabs(['Fee Totals', 'Fee Percentages'])

    with fee_amt_tab:
        col_ps, col_pm = st.columns(2)
        
        st.subheader('Fees By Payment Source')
        fee_ps_fig = st.bar_chart(
                        df_selection_fee.groupby(['PAYMENT_SOURCE', 'PAYMENT_METHOD'])['FEE_AMOUNT'].sum().reset_index(),
                        y = 'FEE_AMOUNT',
                        x = 'PAYMENT_SOURCE',
                        color = 'PAYMENT_METHOD')
        
        st.subheader('Fees By Payment Method')
        fee_pm_fig = st.bar_chart(
                        df_selection_fee.groupby(['PAYMENT_METHOD_SUB', 'PAYMENT_BRAND'])['FEE_AMOUNT'].sum().reset_index(),
                        y = 'FEE_AMOUNT',
                        x = 'PAYMENT_METHOD_SUB',
                        color = 'PAYMENT_BRAND', )
    
            
    with fee_pct_tab:
        col_ps, col_pm = st.columns(2)

        st.subheader('Average Fee % By Payment Source')
        fee_ps_fig = st.bar_chart(
                        df_selection_fee.groupby(['PAYMENT_SOURCE', 'PAYMENT_METHOD'])['FEE_PERCENTAGE'].mean().reset_index(),
                        y = 'FEE_PERCENTAGE',
                        x = 'PAYMENT_SOURCE',
                        color = 'PAYMENT_METHOD')

        st.subheader('Average Fee % By Payment Method')
        fee_pm_fig = st.bar_chart(
                        df_selection_fee.groupby(['PAYMENT_METHOD_SUB', 'PAYMENT_BRAND'])['FEE_PERCENTAGE'].mean().reset_index(),
                        y = 'FEE_PERCENTAGE',
                        x = 'PAYMENT_METHOD_SUB',
                        color = 'PAYMENT_BRAND')