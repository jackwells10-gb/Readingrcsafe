import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION ---
# Example: Reading Bridge, River Thames (Station ID: 7058)
# Find your station ID at: https://environment.data.gov.uk/flood-monitoring/id/stations
STATION_ID = "7058" 
LAT, LON = 51.45, -0.97  # Reading, UK

st.set_page_config(page_title="Club Rowing Dashboard", layout="wide")

# --- DATA FETCHING ---
def get_river_data(station_id):
    url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/{station_id}/readings?_sorted&_limit=48"
    response = requests.get(url).json()
    items = response['items']
    df = pd.DataFrame(items)
    df['dateTime'] = pd.to_datetime(df['dateTime'])
    return df

def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,wind_speed_10m,wind_gusts_10m&forecast_days=1"
    res = requests.get(url).json()
    return res

# --- DASHBOARD UI ---
st.title("🛶 Rowing Safety Dashboard")

river_df = get_river_data(STATION_ID)
weather = get_weather_data(LAT, LON)

current_level = river_df['value'].iloc[0]
current_wind = weather['hourly']['wind_speed_10m'][0]
current_gust = weather['hourly']['wind_gusts_10m'][0]

# --- 1. SAFETY FLAG LOGIC ---
if current_level > 2.5 or current_gust > 25:
    st.error("### 🚩 RED FLAG: HIGH WATER / WIND")
elif current_level > 1.8 or current_gust > 15:
    st.warning("### 🚩 AMBER FLAG: SENIOR CREWS ONLY")
else:
    st.success("### 🏳️ GREEN FLAG: ALL SQUADS CLEAR")

# --- 2. KPI METRICS ---
col1, col2, col3 = st.columns(3)
col1.metric("River Level", f"{current_level} m", delta=round(current_level - river_df['value'].iloc[4], 2))
col2.metric("Wind Speed", f"{current_wind} km/h")
col3.metric("Wind Gusts", f"{current_gust} km/h")

# --- 3. CHARTS ---
st.divider()
left_chart, right_chart = st.columns(2)

with left_chart:
    st.subheader("River Level (Last 24h)")
    fig_river = px.line(river_df, x='dateTime', y='value', labels={'value': 'Level (m)', 'dateTime': 'Time'})
    st.plotly_chart(fig_river, use_container_width=True)

with right_chart:
    st.subheader("Wind Forecast (Today)")
    wind_df = pd.DataFrame({
        "Time": pd.to_datetime(weather['hourly']['time']),
        "Wind": weather['hourly']['wind_speed_10m'],
        "Gusts": weather['hourly']['wind_gusts_10m']
    })
    fig_weather = px.line(wind_df, x='Time', y=['Wind', 'Gusts'], labels={'value': 'km/h'})
    st.plotly_chart(fig_weather, use_container_width=True)
