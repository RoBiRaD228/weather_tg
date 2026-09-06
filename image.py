import os
from html2image import Html2Image

hti = Html2Image()
hti.output_path = "temp"
os.makedirs("temp", exist_ok=True)

async def generate_weather_widget(city: str, current_temp: str, app_temp: str, weather: str, user_id: int) -> str:
    html_code = f"""
<!DOCTYPE html>
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
    padding: 24px 28px;

    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

.city_and_temp {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.city {{
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
}}

.temp {{
    font-size: 42px;
    font-weight: 800;
    line-height: 1;
}}

.weather {{
    font-size: 20px;
    font-weight: 500;
    opacity: 0.9;
    margin-top: -10px;
}}

.temp_row {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    background: rgba(255, 255, 255, 0.15);
    padding: 8px 14px;
    border-radius: 12px;
    width: fit-content;
    backdrop-filter: blur(10px);
}}

.text_app_temp {{
    font-style: normal;
    opacity: 0.8;
}}

.app_temp {{
    font-weight: 700;
}}
</style>
<body>
    <div class="card">
        <div class="city_and_temp">
            <div class="city">{city}</div>
            <div class="temp">({current_temp} °C)</div>
        </div>
        <div class="temp_row">
            <div class="text_app_temp">Ощущается как</div>
            <div class="app_temp">{app_temp} °C</div>
        </div>
        <div class="weather">{weather}</div>
    </div>
</body>
</html>
    """

    file_path = os.path.join("temp", f"{user_id}_weather_card.png")
    
    # Размер уменьшен до 370x220, так как карточка стала ниже
    hti.screenshot(
        html_str=html_code, 
        save_as=f"{user_id}_weather_card.png", 
        size=(380, 220)
    )
    return file_path

async def generate_weather_widget_three_days(city: str, current_temp_list: list, app_current_temp_list: list, weather_list: list, third_day: str, user_id: int):
    html_code = f"""
<!DOCTYPE html>
<html lang="ru">
<style>
    body {{
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

.card {{
    width: 520px;
    height: 250px;
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
    padding: 0px 24px;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}}

.city {{
    font-size: 26px;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}}

.subtitle {{
    font-size: 13px;
    opacity: 0.75;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.forecast_grid {{
    display: flex;
    gap: 12px;
}}

.day_column {{
    flex: 1;
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 18px;
    padding: 14px 10px;
    
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    justify-content: space-between;
}}

.day_name {{
    font-size: 14px;
    font-weight: 600;
    opacity: 0.9;
}}

.temp {{
    font-size: 30px;
    font-weight: 800;
    margin: 6px 0;
    line-height: 1;
}}

.weather {{
    font-size: 13px;
    font-weight: 500;
    opacity: 0.85;
    margin-bottom: 6px;
}}

.app_temp {{
    font-size: 11px;
    opacity: 0.7;
    background: rgba(0, 0, 0, 0.15);
    padding: 4px 8px;
    border-radius: 8px;
}}
</style>
<body>
    <div class="card">
        <div class="header">
            <h1 class="city">{city}</h1>
            <span class="subtitle">Прогноз на 3 дня</span>
        </div>
        <div class="forecast_grid">
            <div class="day_column">
                <div class="day_name">Сегодня</div>
                <div class="temp">{current_temp_list[0]}°C</div>
                <div class="weather">{weather_list[0]}</div>
                <div class="app_temp">ощущ. как {app_current_temp_list[0]}°C</div>
            </div>
            <div class="day_column">
                <div class="day_name">Завтра</div>
                <div class="temp">{current_temp_list[1]}°C</div>
                <div class="weather">{weather_list[1]}</div>
                <div class="app_temp">ощущ. как {app_current_temp_list[1]}°C</div>
            </div>
            <div class="day_column">
                <div class="day_name">{third_day}</div>
                <div class="temp">{current_temp_list[2]}°C</div>
                <div class="weather">{weather_list[2]}</div>
                <div class="app_temp">ощущ. как {app_current_temp_list[2]}°C</div>
            </div>

        </div>
    </div>
</body>
</html>
"""

    file_path = os.path.join("temp", f"{user_id}_weather_card.png")
    # Размер уменьшен до 370x220, так как карточка стала ниже
    hti.screenshot(
        html_str=html_code, 
        save_as=f"{user_id}_weather_card.png", 
        size=(520, 250)
    )
    return file_path