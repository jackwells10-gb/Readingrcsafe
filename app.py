import streamlit as st
import requests
import pandas as pd

# --- CONFIGURATION ---
# Replace with your local Station ID (e.g., '2200TH' for Reading)
STATION_ID = "2200TH" 
LAT, LON = 51.45, -0.97

st.set_page_config(page_title="Rowing Club Dashboard", layout="wide")

# --- DATA FETCHING ---
@st.cache_data(ttl=600)
def get_river_metrics(station_id):
    url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/{station_id}/measures"
    try:
        items = requests.get(url).json().get('items', [])
        data = {"flow": None, "level": None}
        for item in items:
            if item['parameter'] == 'flow':
                data['flow'] = item['latestReading']['value']
            if item['parameter'] == 'level':
                data['level'] = item['latestReading']['value']
        return data
    except:
        return {"flow": None, "level": None}

@st.cache_data(ttl=600)
def get_weather_metrics(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=wind_gusts_10m"
    res = requests.get(url).json()
    return res['current_weather'], res['hourly']

# --- LOAD DATA ---
river = get_river_metrics(STATION_ID)
weather_now, weather_hourly = get_weather_metrics(LAT, LON)

# --- UI LAYOUT ---
st.title("🛶 Club Safety Dashboard")

# TOP ROW: THE KPI TILES
col1, col2, col3,
