import pandas as pd
import requests


def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": ",".join(map(str, latitude)),
        "longitude": ",".join(map(str, longitude)),
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "weather_code"
        ],
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def weather_to_df(data):
    records = []
    for loc in data:
        daily = loc["daily"]
        n_days = len(daily["time"])
        for i in range(n_days):
            records.append({
                "lat": loc["latitude"],
                "lng": loc["longitude"],
                "date": daily["time"][i],
                "temperature_2m_max": daily["temperature_2m_max"][i],
                "temperature_2m_min": daily["temperature_2m_min"][i],
                "precipitation_sum": daily["precipitation_sum"][i],
                "precipitation_probability_max": daily["precipitation_probability_max"][i],
                "wind_speed_10m_max": daily["wind_speed_10m_max"][i],
                "wind_gusts_10m_max": daily["wind_gusts_10m_max"][i],
                "weather_code": daily["weather_code"][i],
            })
    return pd.DataFrame(records)


cities = pd.read_csv("data.csv")

data = get_weather(cities["lat"].tolist(), cities["lng"].tolist())
df = weather_to_df(data)

df.to_csv("bronze/raw.csv",index=False)   