import streamlit as st
import requests

# --- CONFIGURATION ---
STATION_ID = "2200TH"
FLOW_MEASURE_ID = "2200TH-flow--Mean-15_min-m3_s"
LAT, LON = 51.458, -0.967 

st.set_page_config(page_title="Reading Rowing Club safety Dashboard", layout="wide")

# --- DATA FETCHING ---
@st.cache_data(ttl=600)
def get_reading_flow():
    url = f"https://environment.data.gov.uk/flood-monitoring/id/measures/{FLOW_MEASURE_ID}"
    try:
        res = requests.get(url).json()
        return res['items']['latestReading']['value']
    except:
        return None

@st.cache_data(ttl=600)
def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=wind_gusts_10m,uv_index&daily=sunrise,sunset&timezone=Europe%2FLondon"
    try:
        res = requests.get(url).json()
        return res
    except:
        return None

# --- LOAD DATA ---
current_flow = get_reading_flow()
weather = get_weather_data(LAT, LON)

# --- UI LAYOUT ---
st.title(" Reading Rowing Club safety Dashboard")

if weather:
    weather_now = weather['current_weather']
    gust_now = weather['hourly']['wind_gusts_10m'][0]
    uv_now = weather['hourly']['uv_index'][0]
    sunrise_time = weather['daily']['sunrise'][0].split('T')[1]
    sunset_time = weather['daily']['sunset'][0].split('T')[1]

    # TOP ROW: MAIN METRICS
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        flow_val = f"{current_flow} m³/s" if current_flow is not None else "Offline"
        st.metric("River Flow", flow_val)
        
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
        st.subheader("Safety Status")
        if current_flow:
            if current_flow > 100:
                st.error("RED FLAG: NO ROWING. Flow is dangerously high.")
            elif current_flow > 75:
                st.warning("AMBER FLAG: SENIOR CREWS ONLY. High flow, exercise caution.")
            else:
                st.success("GREEN FLAG: ALL SQUADS CLEAR. Conditions are normal.")
        else:
            st.info("Flow data unavailable. Check Caversham Lock gauges manually.")

    with right_col:
        st.subheader("Light & UV Index")
        sun1, sun2, sun3 = st.columns(3)
        
        with sun1:
            st.metric("Sunrise", sunrise_time)
        with sun2:
            st.metric("Sunset", sunset_time)
        with sun3:
            uv_label = "Low"
            if uv_now >= 6: uv_label = "High"
            elif uv_now >= 3: uv_label = "Moderate"
            st.metric("UV Index", f"{uv_now} ({uv_label})")

    st.divider()
    st.caption(f"Last update: {weather_now['time'].replace('T', ' ')}")
else:
    st.error("Weather data currently unavailable.")
