import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timezone, timedelta

# import openmeteo_requests
# import pandas as pd
# import requests_cache
# from retry_requests import retry

# cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
# retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
# openmeteo = openmeteo_requests.Client(session = retry_session)

load_dotenv()

api_key = os.getenv("API")

def get_city_parms(city_name, api_key):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city_name,
        "appid": api_key,
        "limit": 1
    }
    try:
        response = requests.get(url, params=params, timeout = 5)
        response.raise_for_status()
        data = response.json()

        # print(data)

        if data == []:
            print(f"Ошибка, город {city_name} не был найден")
            return None, None
        lat = data[0]["lat"]
        lon = data[0]["lon"]

        return lat, lon

    except requests.exceptions.HTTPError as Eror:
        print(f"Ошибка HTTP (неверный город или ключ): {Eror}")

def get_weather(city, api_key):
    lat, lon = get_city_parms(city, api_key)
    if lat == None or lon == None:
        while(True):
            city = input("Введите название города: ")
            lat, lon = get_city_parms(city, api_key)
            if lat != None and lon != None:
                break
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "hourly": ["temperature_2m","weather_code", "apparent_temperature"]
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)
    offset_seconds = data["utc_offset_seconds"]

    now_utc = datetime.now(timezone.utc)
    user_time = now_utc + timedelta(seconds=offset_seconds)
    print(user_time.strftime("%H:%M"))

    hourly_data = data["hourly"]

    time = hourly_data["time"]
    temperature = hourly_data["temperature_2m"]
    weather_code = hourly_data["weather_code"]

    now = datetime.now()
    hour = now.hour

    # print(hour)

    match weather_code[hour]:
        case 0:
            weather = "Ясно"
        case 1:
            weather = "Преимущественно ясно"
        case 2:
            weather = "переменная облачность"
        case 3:
            weather = "пасмурно"
        case 45:
            weather = "Туман"
        case 48:
            weather = "Иней с выпадением осадков"
        case 51:
            weather = "Легкий струйный полив"
        case 53:
            weather = "Средний струйный полив"
        case 55:
            weather = "Плотный струйный полив"
        case 56:
            weather = "Легкий ледяной дождь"
        case 57:
            weather = "Насыщенный ледяной дождь"
        case 61:
            weather = "Слабый дождь"
        case 63:
            weather = "Умеренный дождь"
        case 65:
            weather = "Сильный дождь"
        case 66:
            weather = "Слабый ледяной дождь"
        case 67:
            weather = "Сильный ледяной дождь"
        case 71:
            weather = "Слабый снегопад"
        case 73:
            weather = "Умеренный снегопад"
        case 75:
            weather = "Сильный снегопад"
        case 77:
            weather = "Зерна снега"
        case 80:
            weather = "Слабые дожди"
        case 81:
            weather = "Умеренные дожди"
        case 82:
            weather = "Сильные дожди"
        case 85:
            weather = "Слабые снежные осадки"
        case 86:
            weather = "Сильные снежные осадки"
        case _:
            weather = "Неизвестные погодные условия"

    print(f"Сейчас в {city} температура равна {temperature[hour]}, погода {weather}")


if __name__ == "__main__":
    city = input("Введите название города: ")
    get_weather(city, api_key)