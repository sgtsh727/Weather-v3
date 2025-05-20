
import streamlit as st
import requests
import math
import json
from datetime import date

# Load ballpark data
with open("ballparks_data.json", "r") as f:
    ballparks = json.load(f)

API_KEY = "8f0513552fb991ad098623e6d79f8426"
MLB_SCHEDULE_API = "https://statsapi.mlb.com/api/v1/schedule"

def fetch_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def wind_relative_direction(wind_deg, park_orientation):
    angle = (wind_deg - park_orientation + 360) % 360
    if angle <= 45 or angle >= 315:
        return "blowing out"
    elif 135 <= angle <= 225:
        return "blowing in"
    elif 45 < angle < 135:
        return "blowing toward right field"
    else:
        return "blowing toward left field"

def wind_arrow(angle):
    arrows = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖']
    return arrows[round(angle % 360 / 45) % 8]

def get_todays_venues():
    today = date.today().strftime("%Y-%m-%d")
    params = {"sportId": 1, "date": today}
    response = requests.get(MLB_SCHEDULE_API, params=params)
    if response.status_code != 200:
        return set()
    data = response.json()
    venues = set()
    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            venue = game.get("venue", {}).get("name")
            if venue:
                venues.add(venue)
    return venues

st.set_page_config(page_title="MLB Ballpark Weather", layout="wide")
st.title("MLB Ballpark Weather Tracker")

today_venues = get_todays_venues()
filtered_ballparks = {k: v for k, v in ballparks.items() if k in today_venues}

if not filtered_ballparks:
    st.warning("No MLB games scheduled today.")
else:
    for park, data in filtered_ballparks.items():
        weather = fetch_weather(*data["coords"])
        if not weather:
            continue

        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(data["logo"], width=60)
        with col2:
            st.subheader(park)
            if data["indoor"]:
                st.markdown("**Stadium is indoor - weather not applicable**", help="Indoor or retractable roof likely closed.")
            else:
                temp = weather["main"]["temp"]
                humidity = weather["main"]["humidity"]
                wind_speed = weather["wind"]["speed"]
                wind_deg = weather["wind"]["deg"]
                direction = wind_relative_direction(wind_deg, data["orientation"])
                arrow = wind_arrow((wind_deg - data["orientation"]) % 360)

                st.write(f"**Temperature:** {temp}°F")
                st.write(f"**Humidity:** {humidity}%")
                st.write(f"**Wind:** {wind_speed} mph {arrow} ({direction})")
