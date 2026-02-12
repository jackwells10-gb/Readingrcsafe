# --- DATA FETCHING (Updated for m/s) ---
@st.cache_data(ttl=600)
def get_weather_data(lat, lon):
    # Added windspeed_unit=ms to the API call
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=wind_gusts_10m,uv_index&daily=sunrise,sunset&windspeed_unit=ms&timezone=Europe%2FLondon"
    try:
        res = requests.get(url, timeout=10).json()
        return res
    except Exception:
        return None

# ... (rest of your logic) ...

if weather:
    current_hour_idx = datetime.now().hour
    weather_now = weather['current_weather']
    # Values are now in m/s thanks to the API parameter
    wind_now = weather_now['windspeed']
    gust_now = weather['hourly']['wind_gusts_10m'][current_hour_idx]

    # TOP ROW: MAIN METRICS
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        flow_val = f"{current_flow} m³/s" if current_flow is not None else "Offline"
        st.metric("🌊 Current Flow", flow_val)
    with col2:
        st.metric("🌡️ Air Temp", f"{weather_now['temperature']}°C")
    with col3:
        st.metric("🍃 Wind Speed", f"{wind_now} m/s")
    with col4:
        st.metric("🌪️ Wind Gusts", f"{gust_now} m/s")
