import asyncio
import aiohttp

import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timezone, timedelta

import math

load_dotenv()

api_key = os.getenv("API")

async def get_city_parms(city_name, api_key):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city_name,
        "appid": api_key,
        "limit": 1
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
        
        if data == []:
            print(f"Ошибка, город {city_name} не был найден")
            return None, None
        lat = data[0]["lat"]
        lon = data[0]["lon"]

        return lat, lon

    except requests.exceptions.HTTPError as Eror:
        print(f"Ошибка HTTP (неверный город или ключ): {Eror}")

async def get_weather(city, api_key):
    lat, lon = await get_city_parms(city, api_key)
    if lat == None or lon == None:
        return None
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "hourly": ["temperature_2m","weather_code", "apparent_temperature"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            return data

async def weather_code_string(weather_code):
    match weather_code:
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

    return weather

async def get_weather_new(data):
    hourly_data = data["hourly"]

    time = hourly_data["time"]
    temperature = hourly_data["temperature_2m"]
    weather_code = hourly_data["weather_code"]
    app_temperature = hourly_data["apparent_temperature"]

    offset_seconds = data["utc_offset_seconds"]

    now_utc = datetime.now(timezone.utc)
    user_time = now_utc + timedelta(seconds=offset_seconds)

    hour = user_time.hour

    weather = await weather_code_string(weather_code[hour])

    message = f"Сейчас температура {temperature[hour]} (ощущается как {app_temperature[hour]}), погода {weather}"

    return message

async def get_weather_day(data):
    hourly_data = data["hourly"]

    time = hourly_data["time"]
    temperature = hourly_data["temperature_2m"]
    weather_code = hourly_data["weather_code"]
    app_temperature = hourly_data["apparent_temperature"]

    message = "Погода на сегодня: "

    for i in  range(24):
        hour_min = datetime.fromisoformat(time[i])
        hour_min = hour_min.strftime("%H:%M")

        weather = await weather_code_string(weather_code[i])

        message += f"\n{hour_min} - {temperature[i]} °C ({app_temperature[i]} °C), {weather}"
    
    return message

async def get_weather_three_day(data):
    hourly_data = data["hourly"]

    time = hourly_data["time"]
    temperature = hourly_data["temperature_2m"]
    weather_code = hourly_data["weather_code"]
    app_temperature = hourly_data["apparent_temperature"]

    message = "Погода на 3 дня:\n"

    for i in  range(3):
        today_temp = temperature[(i * 24):(24 * (i + 1))]
        today_app_temp = app_temperature[(i * 24):(24 * (i + 1))]
        today_weather = weather_code[(i * 24):(24 * (i + 1))]

        max_temp = max(today_temp)
        min_temp = min(today_temp)

        max_app_temp = max(today_app_temp)
        min_app_temp = min(today_app_temp)

        most_weather_code = max(today_weather, key = today_weather.count)

        day = datetime.fromisoformat(time[i * 24])
        day = day.strftime("%d.%m")

        weather = await weather_code_string(most_weather_code)

        message += f"\n{day} - макс. {max_temp} °C, мин. {min_temp} °C, {weather}\n"
    
    return message