import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Simulate data
np.random.seed(42)
days = pd.date_range(end=pd.Timestamp.today(), periods=7)
data = {
    "Date": days,
    "Air Quality Index": np.random.randint(50, 150, size=7),
    "Water Usage (liters)": np.random.randint(100000, 200000, size=7),
    "Electricity Consumption (kWh)": np.random.randint(5000, 10000, size=7),
    "Waste Generated (tons)": np.random.uniform(20, 50, size=7).round(2)
}
df = pd.DataFrame(data)

# Streamlit App
st.set_page_config(page_title="City Health Dashboard", layout="wide")
st.title("🌆 City Health Dashboard - Kakinada")

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Today's AQI", f"{df['Air Quality Index'].iloc[-1]}")
col2.metric("Water Usage", f"{df['Water Usage (liters)'].iloc[-1]:,} L")
col3.metric("Power Usage", f"{df['Electricity Consumption (kWh)'].iloc[-1]:,} kWh")
col4.metric("Waste Collected", f"{df['Waste Generated (tons)'].iloc[-1]} tons")

# Line Chart
st.subheader("📈 Trends Over the Past Week")
chart = alt.Chart(df).transform_fold(
    ['Air Quality Index', 'Water Usage (liters)', 'Electricity Consumption (kWh)', 'Waste Generated (tons)']
).mark_line(point=True).encode(
    x='Date:T',
    y='value:Q',
    color='key:N'
).properties(width=800, height=400)

st.altair_chart(chart, use_container_width=True)

# Table
st.subheader("📋 Raw Data")
st.dataframe(df)
