
import streamlit as st
import requests
import math
import json
from datetime import datetime

# Load ballpark data
with open("ballparks_data.json", "r") as f:
    ballparks = json.load(f)

API_KEY = "8f0513552fb991ad098623e6d79f8426"

# Map team names to their stadium names as used in ballparks_data.json
team_to_park = {{
    "BOS": "Fenway Park",
    "NYY": "Yankee Stadium",
    "TOR": "Rogers Centre",
    "BAL": "Camden Yards",
    "TB": "Tropicana Field (Steinbrenner Field)",
    "CLE": "Progressive Field",
    "DET": "Comerica Park",
    "KC": "Kauffman Stadium",
    "MIN": "Target Field",
    "CWS": "Guaranteed Rate Field",
    "HOU": "Minute Maid Park",
    "TEX": "Globe Life Field",
    "SEA": "T-Mobile Park",
    "LAA": "Angel Stadium",
    "OAK": "Oakland Athletics (Sutter Health Park)",
    "SF": "Oracle Park",
    "LAD": "Dodger Stadium",
    "SD": "Petco Park",
    "ARI": "Chase Field",
    "COL": "Coors Field",
    "CHC": "Wrigley Field",
    "CIN": "Great American Ball Park",
    "MIL": "Miller Park",
    "PIT": "PNC Park",
    "STL": "Busch Stadium",
    "ATL": "Truist Park",
    "MIA": "LoanDepot Park",
    "NYM": "Citi Field",
    "WSH": "Nationals Park",
    "PHI": "Citizens Bank Park"
}}

def fetch_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={{lat}}&lon={{lon}}&appid={{API_KEY}}&units=imperial"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_today_ballparks():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={{today}}"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    data = response.json()
    parks = set()
    for date in data.get("dates", []):
        for game in date.get("games", []):
            home = game["teams"]["home"]["team"]["abbreviation"]
            park = team_to_park.get(home)
            if park:
                parks.add(park)
    return list(parks)

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

st.set_page_config(page_title="MLB Ballpark Weather", layout="wide")
st.title("MLB Ballpark Weather Tracker")

active_parks = fetch_today_ballparks()
if not active_parks:
    st.warning("No MLB games scheduled for today or unable to fetch schedule.")
else:
    for park in active_parks:
        data = ballparks.get(park)
        if not data:
            continue

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

                st.write(f"**Temperature:** {{temp}}°F")
                st.write(f"**Humidity:** {{humidity}}%")
                st.write(f"**Wind:** {{wind_speed}} mph {{arrow}} ({{direction}})")
