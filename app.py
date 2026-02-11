import streamlit as st
import requests

# --- CONFIGURATION ---
# Specifically for Reading Bridge (River Thames)
STATION_ID = "2200TH"
FLOW_MEASURE_ID = "2200TH-flow--Mean-15_min-m3_s"
LAT, LON = 51.458, -0.967 # Reading Bridge coordinates

st.set_page_config(page_title="Reading RC Dashboard", layout="wide")

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
def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=wind_gusts_10m"
    res = requests.get(url).json()
    return res

# --- LOAD DATA ---
current_flow = get_reading_flow()
weather_data = get_weather(LAT, LON)
weather_now = weather_data['current_weather']
gust_now = weather_data['hourly']['wind_gusts_10m'][0]

# --- UI ---
st.title("🛶 Reading Bridge Rowing Dashboard")

# TOP ROW
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

# --- SAFETY LOGIC (Reading RC Thresholds) ---
st.subheader("Safety Status")

if current_flow:
    # Typical Reading thresholds: >100 Red, >75 Amber
    if current_flow > 100:
        st.error("### 🚩 RED FLAG: NO ROWING\nFlow is dangerously high.")
    elif current_flow > 75:
        st.warning("### 🚩 AMBER FLAG: SENIOR CREWS ONLY\nHigh flow. No novices or small boats.")
    else:
        st.success("### 🏳️ GREEN FLAG: ALL SQUADS CLEAR\nConditions are normal.")
else:
    st.info("Flow data currently unavailable from EA. Please check Caversham Lock levels manually.")

st.caption(f"Last API Update: {weather_now['time'].replace('T', ' ')}")
