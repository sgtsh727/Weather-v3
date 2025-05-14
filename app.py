import streamlit as st
import requests
import json
import statsapi
from datetime import datetime

API_KEY = "8f0513552fb991ad098623e6d79f8426"

# Load ballpark data
with open("ballparks_data.json", "r") as f:
    ballparks = json.load(f)

# Map stadium names to ballpark keys
def get_park_key_by_venue(venue_name):
    for park, data in ballparks.items():
        if data.get("venue") == venue_name:
            return park
    return None

def fetch_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_game_time_forecast(forecast_list, game_time):
    closest = min(forecast_list, key=lambda x: abs(datetime.strptime(x["dt_txt"], "%Y-%m-%d %H:%M:%S") - game_time))
    return closest

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

# Get today's games
today = datetime.now().strftime('%Y-%m-%d')
games_today = statsapi.schedule(start_date=today, end_date=today)

st.set_page_config(page_title="Welcome to the Weatherhouse", layout="wide")
st.markdown("<h1 style=\"color:#FFD700;font-family:'Courier New', Courier, monospace;font-weight:bold;text-shadow:2px 2px #000000;\">Welcome to the Weatherhouse</h1>", unsafe_allow_html=True)

for game in games_today:
    venue_name = game['venue_name']
    game_time = datetime.strptime(game['game_datetime'], '%Y-%m-%dT%H:%M:%SZ')
    park_key = get_park_key_by_venue(venue_name)
    
    if not park_key or park_key not in ballparks:
        continue

    data = ballparks[park_key]
    forecast = fetch_forecast(*data["coords"])
    if not forecast:
        continue

    game_forecast = get_game_time_forecast(forecast["list"], game_time)

    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(data["logo"], width=60)
    with col2:
        st.subheader(f"{game['away_name']} at {game['home_name']} - {park_key}")
        if data["indoor"]:
            st.markdown("**Stadium is indoor - weather not applicable**")
        else:
            temp = game_forecast["main"]["temp"]
            description = game_forecast["weather"][0]["description"].capitalize()
            wind_speed = game_forecast["wind"]["speed"]
            wind_deg = game_forecast["wind"]["deg"]
            direction = wind_relative_direction(wind_deg, data["orientation"])
            arrow = wind_arrow((wind_deg - data["orientation"]) % 360)

            st.write(f"**Game Time:** {game_time.strftime('%I:%M %p')} UTC")
            st.write(f"**Forecast Temperature:** {temp}°F")
            st.write(f"**Conditions:** {description}")
            st.write(f"**Wind:** {wind_speed} mph {arrow} ({direction})")
