import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURATION ---
STATION_ID = "2200TH"
FLOW_MEASURE_ID = "2200TH-flow--Mean-15_min-m3_s"
LAT, LON = 51.458, -0.967 

st.set_page_config(page_title="Reading Bridge Rowing Dashboard", layout="wide")

# --- DATA FETCHING ---

@st.cache_data(ttl=3600)
def get_historical_flow():
    """Fetches flow data for the last 30 days."""
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    url = f"https://environment.data.gov.uk/flood-monitoring/id/measures/{FLOW_MEASURE_ID}/readings?since={thirty_days_ago}&_sorted"
    try:
        res = requests.get(url, timeout=10).json()
        df = pd.DataFrame(res['items'])
        df['dateTime'] = pd.to_datetime(df['dateTime'])
        df = df.rename(columns={'value': 'Flow (m³/s)'})
        return df[['dateTime', 'Flow (m³/s)']]
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_reading_flow():
    """Fetches the most recent river flow reading with robust error handling."""
    url = f"https://environment.data.gov.uk/flood-monitoring/id/measures/{FLOW_MEASURE_ID}"
    try:
        res = requests.get(url, timeout=10).json()
        items = res.get('items', {})
        
        # The API sometimes returns a list of one item, sometimes just the item
        if isinstance(items, list) and len(items) > 0:
            latest = items[0].get('latestReading', {})
        else:
            latest = items.get('latestReading', {})
            
        value = latest.get('value')
        timestamp = latest.get('dateTime')
        
        return (float(value), timestamp) if value is not None else (None, None)
    except Exception as e:
        return None, None

@st.cache_data(ttl=600)
def get_weather_data(lat, lon):
    """Fetches weather data with wind units set to m/s."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=wind_gusts_10m,uv_index&daily=sunrise,sunset&windspeed_unit=ms&timezone=Europe%2FLondon"
    try:
        res = requests.get(url, timeout=10).json()
        return res
    except Exception:
        return None

# --- LOAD DATA ---
current_flow, flow_time = get_reading_flow()
weather = get_weather_data(LAT, LON)
history_df = get_historical_flow()

# --- LOGIC: SAFETY FLAG ---
# We use the flow thresholds (75 and 100) to set the banner color
flag_color = "#808080" # Default Gray
flag_text = "DATA OFFLINE"

if current_flow is not None:
    if current_flow > 120:
        flag_color = "#000000" # black
        flag_text = "😢 BLACK FLAG: NO ROWING"
    elif current_flow > 100:
        flag_color = "#d32f2f" # Red
        flag_text = "🔴 RED FLAG: DANGER, SIGNED OFF, EXPERIENCED CREWS ONLY"    
    elif current_flow > 75:
        flag_color = "#f57c00" # Amber
        flag_text = "🟠 AMBER FLAG: EXPERIENCED CREWS ONLY"
    else:
        flag_color = "#388e3c" # Green
        flag_text = "🟢 GREEN FLAG: ALL SQUADS CLEAR"

# --- UI LAYOUT ---
# Hero Safety Banner
st.markdown(f"""
    <div style="background-color:{flag_color}; padding:25px; border-radius:15px; text-align:center; margin-bottom:20px;">
        <h1 style="color:white; margin:0; font-family:sans-serif;">{flag_text}</h1>
        <p style="color:white; opacity:0.9; margin:5px 0 0 0;">Reading Rowing Club • Reading Bridge Station</p>
    </div>
    """, unsafe_allow_html=True)

if weather:
    current_hour_idx = datetime.now().hour
    weather_now = weather['current_weather']
    gust_now = weather['hourly']['wind_gusts_10m'][current_hour_idx]
    uv_now = weather['hourly']['uv_index'][current_hour_idx]
    
    sunrise_time = weather['daily']['sunrise'][0].split('T')[1]
    sunset_time = weather['daily']['sunset'][0].split('T')[1]

    # MAIN METRICS ROW
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        flow_display = f"{current_flow} m³/s" if current_flow is not None else "Offline"
        st.metric("🌊 River Flow", flow_display)
        if flow_time:
            # Clean up timestamp for display
            clean_time = flow_time.replace('T', ' ').replace('Z', '')[:16]
            st.caption(f"Measured: {clean_time}")
            
    with m2:
        st.metric("🌡️ Air Temp", f"{weather_now['temperature']}°C")
    with m3:
        st.metric("🍃 Wind Speed", f"{weather_now['windspeed']} m/s", f"{weather_now['winddirection']}°")
    with m4:
        st.metric("🌪️ Max Gusts", f"{gust_now} m/s")

    st.divider()

    # SECONDARY INFO ROW
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("🌅 Lighting Conditions")
        s1, s2 = st.columns(2)
        s1.metric("Sunrise", sunrise_time)
        s2.metric("Sunset", sunset_time)

    with col_right:
        st.subheader("⛱️ Sun Safety")
        uv_label = "Low"
        if uv_now >= 6: uv_label = "High"
        elif uv_now >= 3: uv_label = "Moderate"
        st.metric("Current UV Index", f"{uv_now} ({uv_label})")

    st.divider()

    # HISTORICAL GRAPH
    st.subheader("📊 River Flow Trend (30 Days)")
    if not history_df.empty:
        fig = px.line(history_df, x='dateTime', y='Flow (m³/s)', 
                      template="plotly_white",
                      labels={'dateTime': 'Date', 'Flow (m³/s)': 'Flow (m³/s)'})
        
        # Color coding the background for safety thresholds
        fig.add_hrect(y0=100, y1=max(history_df['Flow (m³/s)'].max(), 110), fillcolor="red", opacity=0.1, line_width=0)
        fig.add_hrect(y0=75, y1=100, fillcolor="orange", opacity=0.1, line_width=0)
        
        fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Red Flag Threshold")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Historical data unavailable. Check Environment Agency status.")

    st.caption(f"Last API Sync: {datetime.now().strftime('%H:%M:%S')} | Data source: Environment Agency & Open-Meteo")

else:
    st.error("Unable to connect to weather services. Please check manual club flags.")
