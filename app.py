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
def get_weather_full(lat, lon):
    # Added daily sunrise/sunset and hourly uv_index
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=wind_gusts_10m,uv_index&daily=sunrise,sunset&timezone=Europe%2FLondon"
    res = requests.get(url).json()
    return res

# --- LOAD DATA ---
current_flow = get_reading_flow()
weather_data = get_weather(LAT, LON)
weather_now = weather_data['current_weather']
gust_now = weather_data['hourly']['wind_gusts_10m'][0]

# --- UI ---
st.title("Reading Rowing Club safety Dashboard")

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

# --- SUNLIGHT & UV SECTION ---
st.subheader("☀️ Light & UV Status")

# Extract data from the response
weather_full = get_weather_full(LAT, LON)
sunrise = weather_full['daily']['sunrise'][0].split('T')[1]
sunset = weather_full['daily']['sunset'][0].split('T')[1]
current_uv = weather_full['hourly']['uv_index'][0] # Current hour UV

col_sun1, col_sun2, col_sun3 = st.columns(3)

with col_sun1:
    st.metric("Sunrise (Lights Off)", sunrise)
    st.caption("Standard lighting-up rules apply.")

with col_sun2:
    st.metric("Sunset (Lights On)", sunset)
    st.caption("Ensure kits have reflective gear.")

with col_sun3:
    # UV Index interpretation
    uv_status = "Low"
    if current_uv >= 3: uv_status = "Moderate (Wear Sunscreen)"
    if current_uv >= 6: uv_status = "High (Protection Required)"
    
    st.metric("UV Index", f"{current_uv} ({uv_status})")

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
