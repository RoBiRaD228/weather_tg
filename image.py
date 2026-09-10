import os
import asyncio
from html2image import Html2Image

hti = Html2Image(output_path="temp")
os.makedirs("temp", exist_ok=True)

def _take_screenshot(html_code: str, file_name: str, size: tuple[int, int]) -> str:
    hti.screenshot(
        html_str=html_code, 
        save_as=file_name, 
        size=size
    )
    return os.path.join("temp", file_name)


async def generate_weather_widget(city: str, date_str: str, current_temp: str, app_temp: str, weather: str, user_id: int) -> str:
    icon_svg = get_weather_icon(weather)

    html_code = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}

        .card {{
            width: 380px;
            height: 220px;
            background: linear-gradient(135deg, #4a00e0, #8e2de2);
            color: white;
            box-sizing: border-box;
            padding: 20px 24px;

            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .city_block {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .city {{
            font-size: 22px;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.3px;
        }}

        .date {{
            font-size: 13px;
            font-weight: 500;
            opacity: 0.75;
            padding-left: 8px;
            border-left: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .subtitle {{
            font-size: 11px;
            opacity: 0.6;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            font-weight: 700;
        }}

        .main_info {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 4px;
        }}

        .temp_container {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .temp {{
            font-size: 46px;
            font-weight: 800;
            line-height: 1;
            letter-spacing: -1px;
        }}

        .weather_text {{
            font-size: 15px;
            font-weight: 500;
            opacity: 0.9;
            text-transform: capitalize;
        }}

        .main_icon {{
            width: 76px;
            height: 76px;
            display: flex;
            align-items: center;
            justify-content: center;
            filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.15));
        }}

        .main_icon svg {{
            width: 100%;
            height: 100%;
        }}

        .footer {{
            display: flex;
            align-items: center;
        }}

        .app_temp_badge {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 6px 12px;
            border-radius: 10px;
        }}

        .app_temp_label {{
            opacity: 0.8;
        }}

        .app_temp_val {{
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="city_block">
                <h1 class="city">{city}</h1>
                <span class="date">{date_str}</span>
            </div>
            <span class="subtitle">Сейчас</span>
        </div>

        <div class="main_info">
            <div class="temp_container">
                <div class="temp">{current_temp}°C</div>
                <div class="weather_text">{weather}</div>
            </div>
            <div class="main_icon">
                {icon_svg}
            </div>
        </div>

        <div class="footer">
            <div class="app_temp_badge">
                <span class="app_temp_label">Ощущается как</span>
                <span class="app_temp_val">{app_temp}°C</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

    file_name = f"{user_id}_weather_card.png"

    file_path = await asyncio.to_thread(
        _take_screenshot, html_code, file_name, (380, 220)
    )
    return file_path


async def generate_weather_widget_three_days(
    city: str, 
    current_temp_list: list, 
    app_current_temp_list: list, 
    weather_list: list, 
    third_day: str, 
    user_id: int,
    date_str: str = ""
) -> str:
    days_names = ["Сегодня", "Завтра", third_day]
    days_html = ""

    for i in range(3):
        day_name = days_names[i]
        temp = current_temp_list[i]
        app_temp = app_current_temp_list[i]
        weather_text = weather_list[i]
        icon_svg = get_weather_icon(weather_text)

        days_html += f"""
        <div class="day_column">
            <div class="day_name">{day_name}</div>
            <div class="icon">{icon_svg}</div>
            <div class="temp">{temp}°C</div>
            <div class="app_temp">ощущ. как {app_temp}°C</div>
        </div>
        """

    date_html = f'<span class="date">{date_str}</span>' if date_str else ""

    html_code = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}

        .card {{
            width: 520px;
            height: 280px;
            background: linear-gradient(135deg, #4a00e0, #8e2de2);
            color: white;
            box-sizing: border-box;
            padding: 22px 24px;
            box-shadow: 0 15px 30px rgba(74, 0, 224, 0.3);

            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .city_block {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .city {{
            font-size: 22px;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.3px;
        }}

        .date {{
            font-size: 13px;
            font-weight: 500;
            opacity: 0.75;
            padding-left: 8px;
            border-left: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .subtitle {{
            font-size: 11px;
            opacity: 0.6;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            font-weight: 700;
        }}

        .forecast_grid {{
            display: flex;
            gap: 12px;
            height: 190px;
        }}

        .day_column {{
            flex: 1;
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 18px;
            padding: 12px 8px;
            
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            justify-content: space-between;
        }}

        .day_name {{
            font-size: 13px;
            font-weight: 700;
            opacity: 0.9;
        }}

        .icon {{
            width: 36px;
            height: 36px;
            margin: 2px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.15));
        }}

        .icon svg {{
            width: 100%;
            height: 100%;
        }}

        .temp {{
            font-size: 24px;
            font-weight: 800;
            line-height: 1;
            letter-spacing: -0.5px;
        }}

        .weather {{
            font-size: 12px;
            font-weight: 500;
            opacity: 0.85;
            text-transform: capitalize;
            line-height: 1.2;
            max-height: 2.4em;
            overflow: hidden;
        }}

        .app_temp {{
            font-size: 10px;
            opacity: 0.75;
            background: rgba(0, 0, 0, 0.15);
            padding: 4px 8px;
            border-radius: 8px;
            white-space: nowrap;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="city_block">
                <h1 class="city">{city}</h1>
                {date_html}
            </div>
            <span class="subtitle">Прогноз на 3 дня</span>
        </div>

        <div class="forecast_grid">
            {days_html}
        </div>
    </div>
</body>
</html>
"""

    file_name = f"{user_id}_weather_card_3days.png"
    file_path = await asyncio.to_thread(_take_screenshot, html_code, file_name, (520, 280))
    return file_path


def get_weather_icon(weather_str: str) -> str:
    w = str(weather_str).lower()
    if "ясно" in w and "преимущественно" not in w:
        return '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><circle cx="12" cy="12" r="5" fill="white"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42m12.72-12.72l1.42-1.42"/></svg>'
    elif "дождь" in w or "полив" in w:
        return '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M16 13v6m-4-6v6m-4-6v6" stroke-linecap="round"/><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25" opacity="0.8"/></svg>'
    elif "снег" in w or "иней" in w:
        return '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M20 17.58A5 5 0 0 0 18 8h-1.26A8 8 0 1 0 4 16.25"/><path d="M8 16h.01M12 18h.01M16 16h.01M10 21h.01M14 21h.01" stroke-width="3" stroke-linecap="round"/></svg>'
    elif "туман" in w:
        return '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M5 9h14M3 13h18M5 17h14" stroke-linecap="round"/></svg>'
    else:
        return '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" fill="rgba(255,255,255,0.25)"/></svg>'


async def generate_weather_widget_hourly(city: str, date_str: str, current_temp_list: list, app_current_temp_list: list, weather_list: list, user_id: int) -> str:
    hourly_columns_html = ""
    for i in range(24):
        time_str = f"{i:02d}:00"
        temp = current_temp_list[i]
        app_temp = app_current_temp_list[i]
        weather_text = weather_list[i]
        icon_svg = get_weather_icon(weather_text)

        hourly_columns_html += f"""
        <div class="hour_column">
            <div class="time">{time_str}</div>
            <div class="icon">{icon_svg}</div>
            <div class="temp_block">
                <span class="temp">{temp}°</span>
                <span class="app_temp">({app_temp}°)</span>
            </div>
        </div>
        """

    html_code = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}

        .card {{
            width: 520px;
            height: 520px;
            background: linear-gradient(135deg, #4a00e0, #8e2de2);
            color: white;
            box-sizing: border-box;
            padding: 24px;
            box-shadow: 0 15px 30px rgba(74, 0, 224, 0.3);

            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 8px;
        }}

        .city_block {{
            display: flex;
            align-items: baseline;
            gap: 10px;
        }}

        .city {{
            font-size: 24px;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.5px;
        }}

        .date {{
            font-size: 15px;
            font-weight: 500;
            opacity: 0.8;
        }}

        .subtitle {{
            font-size: 12px;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .hourly_grid {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 10px;
        }}

        .hour_column {{
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 14px;
            padding: 8px 4px;
            
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            justify-content: space-between;
        }}

        .time {{
            font-size: 12px;
            font-weight: 700;
            opacity: 0.9;
        }}

        .icon {{
            width: 24px;
            height: 24px;
            margin: 2px 0;
            color: #ffffff;
        }}

        .icon svg {{
            width: 100%;
            height: 100%;
        }}

        .temp_block {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .temp {{
            font-size: 14px;
            font-weight: 800;
            line-height: 1.1;
        }}

        .app_temp {{
            font-size: 10px;
            opacity: 0.65;
            margin-top: 2px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="city_block">
                <h1 class="city">{city}</h1>
                <span class="date">{date_str}</span>
            </div>
            <span class="subtitle">24 часа</span>
        </div>
        <div class="hourly_grid">
            {hourly_columns_html}
        </div>
    </div>
</body>
</html>
"""

    file_name = f"{user_id}_hourly_weather_card.png"

    file_path = await asyncio.to_thread(
        _take_screenshot, html_code, file_name, (520, 520)
    )
    return file_path