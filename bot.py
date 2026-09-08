import asyncio
import logging
import sys
from os import getenv

from typing import Callable, Any

from aiogram import Bot, Dispatcher, html, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile

from weather import get_weather, get_weather_new, get_weather_new_data, get_weather_day, get_weather_three_day, get_weather_three_days_data, get_weather_tomorow, get_weather_data

from db import db

from image import generate_weather_widget, generate_weather_widget_three_days, generate_weather_widget_hourly

wether_api = getenv("API")

token = getenv("BOT_API")

dp = Dispatcher()
router = Router()

class Form(StatesGroup):
    waiting_from_city_new = State()
    waiting_from_city_day = State()
    waiting_from_city_three_day = State()
    waiting_from_update_city = State()
    waiting_from_city_tomorow = State()

async def handle_weather_command(
    message: Message,
    state: FSMContext,
    form_func: Callable[[Any], Any],
    next_state: Any
):
    city = await db.get_user_city(message.from_user.id)
    if city is not None:
        data = await get_weather(city, wether_api)
        if data is not None:
            string = await form_func(data)
            await message.answer(string)
            await state.clear()
            return
    
    await message.answer("Введите название города")
    await state.set_state(next_state)

async def handle_weather_input(
    message: Message,
    state: FSMContext,
    form_func: Callable[[Any], Any]
):
    city = await db.get_user_city(message.from_user.id)
    data = await get_weather(city, wether_api)

    if data is None:
        await message.answer("Такой город не найден, введите его еще раз")
        return

    await db.add_user_city(message.from_user.id, city)
    string = await form_func(data)

    await message.answer(string)
    await state.clear()


@router.message(F.text == "/new")
async def weather_new_ask_city(message: Message, state: FSMContext):
    await handle_weather_command(
        message=message,
        state=state,
        form_func=get_weather_new,
        next_state=Form.waiting_from_city_new
    )

@router.message(Form.waiting_from_city_new)
async def weather_new(message: Message, state: FSMContext):
    await handle_weather_input(
        message=message,
        state=state,
        form_func=get_weather_new
    )

@router.message(F.text == "/day")
async def weather_day_ask_city(message: Message, state: FSMContext) -> None:
    await handle_weather_command(
        message=message,
        state=state,
        form_func=get_weather_day,
        next_state=Form.waiting_from_city_day
    )

@router.message(Form.waiting_from_city_day)
async def weather_day(message: Message, state: FSMContext):
    await handle_weather_input(
        message=message,
        state=state,
        form_func=get_weather_day
    )

@router.message(F.text == "/tomorow")
async def weather_tomorow_ask_city(message: Message, state: FSMContext) -> None:
    await handle_weather_command(
        message=message,
        state=state,
        form_func=get_weather_tomorow,
        next_state=Form.waiting_from_city_tomorow
    )

@router.message(Form.waiting_from_city_tomorow)
async def weather_day(message: Message, state: FSMContext):
    await handle_weather_input(
        message=message,
        state=state,
        form_func=get_weather_tomorow
    )

@router.message(F.text == "/three_days")
async def three_days_ask_city(message: Message, state: FSMContext) -> None:
    await handle_weather_command(
        message=message,
        state=state,
        form_func=get_weather_three_day,
        next_state=Form.waiting_from_city_three_day
    )

@router.message(Form.waiting_from_city_three_day)
async def three_days(message: Message, state: FSMContext):
    await handle_weather_input(
        message=message,
        state=state,
        form_func=get_weather_three_day
    )

async def link_setting_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text= "Изменить город", callback_data= 'update_city')]
    ]

    return InlineKeyboardMarkup(inline_keyboard = inline_kb_list)


@router.message(F.text == "/setting")
async def setting(message: Message) -> None:
    city = await db.get_user_city(message.from_user.id)
    await message.answer(f"""
Ваш город: <b>{city}</b>

Выберите, что хотите сделать:""", reply_markup= await link_setting_kb())

@router.callback_query(F.data == 'update_city')
async def ask_update_city(call: CallbackQuery, state: FSMContext):
    await call.answer("Ожидаю написание города", show_alert=False)
    await call.message.answer("Введите название города")
    await state.set_state(Form.waiting_from_update_city)

@router.message(Form.waiting_from_update_city)
async def update_city(message: Message, state: FSMContext):
    city = message.text
    data = await get_weather(city, wether_api)

    if data == None:
        await message.answer("Такой город не найден, введите город ещё раз")
        return
    
    await db.add_user_city(message.from_user.id, city)
    await message.answer(f"Ваш город был изменен на <b>{city}</b>")

    await state.clear()

@router.message(F.text == '/image')
async def create_image(message: Message):
    city = await db.get_user_city(message.from_user.id)
    data = await get_weather(city, wether_api)

    current_temp, app_current_temp, weather = await get_weather_new_data(data)

    file_path = await generate_weather_widget(city, current_temp, app_current_temp, weather, message.from_user.id)
    image = FSInputFile(file_path)

    await message.answer_photo(photo=image, caption=f"Текущая погода в {city}")

@router.message(F.text == '/image_three')
async def create_three_image(message: Message):
    city = await db.get_user_city(message.from_user.id)
    data = await get_weather(city, wether_api)

    current_temp_list, app_current_temp_list, weather_list, third_day = await get_weather_three_days_data(data)

    file_path = await generate_weather_widget_three_days(city, current_temp_list, app_current_temp_list, weather_list, third_day, message.from_user.id)
    image = FSInputFile(file_path)

    await message.answer_photo(photo=image, caption=f"Погода на 3 дня в {city}")

@router.message(Command("image_day"))
async def create_image_day(message: Message, command: CommandObject):
    args = command.args

    if not args:
        await message.answer("Вы не ввкли число после команды (/image_day 3)")
        return
    
    if not args.isdigit:
        await message.answer("Число должно быть целым (/image_day 3)")
        return
    
    day = int(args)

    city = await db.get_user_city(message.from_user.id)
    data = await get_weather(city, wether_api)

    time_list, temp_list, app_temp_list, weather_list, day_date_str = await get_weather_data(data, day)
    file_path = await generate_weather_widget_hourly(city, day_date_str, temp_list, app_temp_list, weather_list, message.from_user.id)

    image = FSInputFile(file_path)

    await message.answer_photo(photo=image, caption=f"Погода в {city}")

@router.message(CommandStart)
async def command_start(message: Message) -> None:
    await message.answer(f"Привет, {message.from_user.full_name}" +
    """Вот список команд:
/new - Погода в данный момент
/day - Погода на день
/three_days - Погода на три дня
/setting - Настройки""")

async def main() -> None:
    await db.connect()
    dp.include_router(router)
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode = ParseMode.HTML))
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())