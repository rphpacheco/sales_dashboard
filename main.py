import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

@st.cache_data
def load_data() -> pd.DataFrame:
    dataframe = pd.read_csv("./sales.csv", index_col=0)
    dataframe["Year"] = dataframe["Year"].astype('string')
    return dataframe

def build_where_clause(filter_results: dict) -> str:
    clause_list = list()
    for column in FILTER_LIST:
        if filter_results[column] != []:
            clause_list.append(f"`{column}` in {filter_results[column]}")
    
    clause_treated = str(clause_list) \
                        .replace('", "',' & ')[1:-1] \
                        .replace('[','(') \
                        .replace(']',')')
    return clause_treated

def set_sidebar(
    dataframe: pd.DataFrame = None, 
    filtered: pd.DataFrame = None) -> dict:
    
    if filtered is None:
        df = dataframe
    else:
        df = filtered

    filter_results = dict()
    for i, name in enumerate(FILTER_LIST):
        component = st.sidebar.multiselect(
            key=i,
            label=name,
            options=df[name].unique(),
            help=f"Select a {name}"
        )
        filter_results.update({str(name) : component})

    return filter_results

def build_visualizations(dataframe: pd.DataFrame):
    st.header(":bar_chart: Sales Dashboard")
    st.markdown("#")
    #### KPIs ####
    total_sales = round(dataframe['Sales'].sum(),2)
    total_customers = len(dataframe["Customer Name"].unique())
    average_ticket = round(total_sales / total_customers, 2)
    sales_by_months = (
        dataframe.groupby(by="Month").sum(numeric_only=True)[["Sales"]].sort_values("Month")
    )
    sales_by_status = (
        dataframe.groupby(by="Status").sum(numeric_only=True)[["Sales"]].sort_values("Sales")
    )
    sales_by_product_line = (
        dataframe.groupby(by="Product Line").sum(numeric_only=True)[["Sales"]].sort_values("Sales")
    )
    sales_by_deal_size = (
        dataframe.groupby(by="Deal Size").sum(numeric_only=True)[["Sales"]].sort_values("Sales")
    )
    #### FIGURES ####
    fig_sales_by_date = px.area(
        sales_by_months,
        title="<b>Sales By Order Date</b>",
        x=sales_by_months.index,
        y="Sales",
        orientation="v",
        color_discrete_sequence=["#FF4B4B"] * len(sales_by_months),
    )

    fig_sales_by_status = px.bar(
        sales_by_status,
        title="<b>Sales By Status</b>",
        x="Sales",
        y=sales_by_status.index,
        orientation="h",
        text="Sales",
        color_discrete_sequence=["#FF4B4B"] * len(sales_by_status),
        width=350
    )
    fig_sales_by_status.update_layout(
        xaxis=dict(
            visible=False
        )
    )

    fig_sales_by_product_line = px.bar(
        sales_by_product_line,
        title="<b>Sales By Product Line</b>",
        x="Sales",
        y=sales_by_product_line.index,
        orientation="h",
        text="Sales",
        color_discrete_sequence=["#FF4B4B"] * len(sales_by_product_line),
        width=500,
    )
    fig_sales_by_product_line.update_layout(
        xaxis=dict(
            visible=False
        )
    )

    fig_sales_by_deal_size = px.pie(
        sales_by_deal_size,
        title="<b>Sales By Deal Size</b>",
        names=sales_by_deal_size.index,
        values="Sales",
        color_discrete_sequence=["#FF4B4B"],
        width=450,
    )

    fig_sales_in_maps = px.choropleth(
        dataframe,
        locations="State", 
        locationmode="USA-states", 
        color="Sales", 
        scope="usa",
        template="plotly_dark",
        width=1150
    )
    fig_sales_in_maps.update_geos(fitbounds="locations", visible=True)
    fig_sales_in_maps.update_layout(
        title="Sales in USA Territory",
        geo=dict(bgcolor= 'rgba(0,0,0,0)', lakecolor="#1f242d"),
        margin={"r":0,"t":25,"l":0,"b":0},
        paper_bgcolor="#1f242d",
        plot_bgcolor="#1f242d",
    )
    ##############
    left_column, middle_column, right_column = st.columns(3)

    with left_column:
        st.markdown('> **Total Sales:**')
        st.subheader(f":orange[$ {total_sales:,}]")

    with middle_column:
        st.markdown("> **Average Ticket:**")
        st.subheader(f":orange[$ {average_ticket:,}]")

    with right_column:
        st.markdown("> **Total Customers:**")
        st.subheader(f":orange[{total_customers:,}]")

    st.markdown("---")

    chart_column1_left,chart_column1_right = st.columns([0.6,0.3])
    
    chart_column1_left.plotly_chart(fig_sales_by_date)
    with chart_column1_right:
        st.plotly_chart(fig_sales_by_status)

    chart_column2_left,chart_column2_right = st.columns(2)
    chart_column2_left.plotly_chart(fig_sales_by_product_line)
    chart_column2_right.plotly_chart(fig_sales_by_deal_size)

    st.plotly_chart(fig_sales_in_maps)
    st.markdown("##")
    st.dataframe(dataframe)

def hide_syle():
    style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)

def main(dataframe):
    
    filter_results = set_sidebar(dataframe=dataframe)
    # print("STATE HERE", filter_results)
    filter_pattern = build_where_clause(filter_results=filter_results)
    # print("FILTER PATTERN", filter_pattern)
    df_selection = dataframe.query(
        expr=eval(filter_pattern),
        engine='python'
    ) if filter_pattern else dataframe
    
    build_visualizations(dataframe=df_selection)
    hide_syle()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Sales Dashboard", 
        page_icon=":bar_chart:",
        initial_sidebar_state="collapsed",
        layout="wide"
    )

    FILTER_LIST = ["Year","Month","Status","Product Line"]

    dataframe = load_data()
    main(dataframe=dataframe)