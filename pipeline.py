import pandas as pd
import requests


def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "weather_code"
        ],
    }

    response = requests.get(url, params=params)

    data = response.json()["daily"]

    df = pd.DataFrame(data)

    return df


cities = pd.read_csv("data.csv")

for index,row in cities.iterrows():
   df = get_weather(cities['lat'][index], cities['lng'][index])
   df.to_csv('bronze/'+row['city']+'.csv',index=False)
