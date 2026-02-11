import streamlit as st
import requests
import pandas as pd

# --- CONFIGURATION ---
# Specifically for Reading Bridge (River Thames)
STATION_ID = "2200TH"
FLOW_MEASURE_ID = "2200TH-flow--Mean-15_min-m3_s"
LAT, LON = 51.458, -0.967 # Reading Bridge coordinates

st.set_page_config(page_title="Reading Bridge Rowing Dashboard", layout="wide")

# --- DATA FETCHING FUNCTIONS ---

@st.cache_data(ttl=600)
def get_reading_flow():
    """Directly targets the flow measure for Reading Bridge."""
    url = f"https://environment.data.gov.uk/flood-monitoring/id/measures/{FLOW_MEASURE_ID}"
    try:
        res = requests.get(url).json()
        return res['items']['latestReading']['value']
    except:
        return None

@st.cache_data(ttl=600)
def get_weather_data(lat, lon):
    """Fetches weather, UV, and sun times from Open-Meteo."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=wind_gusts_10m,uv_index&daily=sunrise,sunset&timezone=Europe%2FLondon"
    try:
        res = requests.get(url).json()
        return res
    except:
        return None

# --- LOAD ALL DATA ---
current_flow = get_reading_flow()
weather = get_weather_data(LAT, LON)

# --- UI LAYOUT ---
st.title("🛶 Reading Bridge Rowing Dashboard")

if weather:
    weather_now = weather['current_weather']
    # Get current hour's gust and UV
    gust_now = weather['hourly']['wind_gusts_10m'][0]
    uv_now = weather['hourly']['uv_index'][0]
    # Get today's sun times
    sunrise = weather['daily']['sunrise'][0].split('T')[1]
    sunset = weather['daily']['sunset'][0].split('T')[1]

    # TOP ROW: MAIN METRICS
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if current_flow:
            st.metric("River Flow", f"{current_flow} m³/s")
        else:
            st.metric("River Flow", "Offline")

    with col2:
        st.metric("Air Temp", f"{weather_now['temperature']}°C")

    with col3:
        st.metric("Wind Speed", f"{weather_now['windspeed']} km/h")

    with col4:
        st.metric("Wind Gusts", f"{gust_now} km/h")

    st.divider()

    # SECOND ROW: SAFETY & LIGHTING
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("🚩 Safety Status")
        if current_flow:
            # Thames Reading thresholds: >100 Red, >75 Amber
            if current_flow > 100:
                st.error("### RED FLAG: NO ROWING\nFlow is dangerously high.")
            elif current_flow > 75:
                st.warning("### AMBER FLAG: SENIOR CREWS ONLY\nHigh flow. Exercise extreme caution.")
            else:
                st.success("### GREEN FLAG: ALL SQUADS CLEAR\nConditions are normal.")
        else:
            st.info("Flow data unavailable. Check Caversham Lock gauges.")

    with right_col:
        st.subheader("☀️ Light & UV")
        sun1, sun2, sun3 = st.columns(3)
        sun1.metric("Sunrise", sunrise)
        sun2.metric("Sunset", sunset)
        
        # UV Interpretation
        uv_status = "Low"
        if uv_now >= 3: uv_status = "Mod (Sunscreen!)"
        if uv_now >= 6: uv_status = "High (Protect!)"
        sun3.metric
