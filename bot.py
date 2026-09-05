import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from weather import get_weather, get_weather_new, get_weather_day, get_weather_three_day

from db import db

wether_api = getenv("API")

token = getenv("BOT_API")

dp = Dispatcher()
router = Router()

class Form(StatesGroup):
    waiting_from_city_new = State()
    waiting_from_city_day = State()
    waiting_from_city_three_day = State()
    waiting_from_update_city = State()

@router.message(F.text == "/new")
async def weather_new_ask_city(message: Message, state: FSMContext):
    city = await db.get_user_city(message.from_user.id)
    if city != None:
        data = await get_weather(city, wether_api)
        string = await get_weather_new(data)

        await message.answer(string)
        await state.clear()

        return

    await message.answer("Введите название города")
    await state.set_state(Form.waiting_from_city_new)

@router.message(Form.waiting_from_city_new)
async def weather_new(message: Message, state: FSMContext):
    city = message.text
    data = await get_weather(city, wether_api)

    if data == None:
        await message.answer("Такой город не найден, введите город ещё раз")
        return

    await db.add_user_city(message.from_user.id, city)
    string = await get_weather_new(data)

    await message.answer(string)
    await state.clear()

@router.message(F.text == "/day")
async def weather_day_ask_city(message: Message, state: FSMContext) -> None:
    city = await db.get_user_city(message.from_user.id)
    if city != None:
        data = await get_weather(city, wether_api)
        string = await get_weather_day(data)

        await message.answer(string)
        await state.clear()

        return

    await message.answer("Введите название города")
    await state.set_state(Form.waiting_from_city_day)

@router.message(Form.waiting_from_city_day)
async def weather_day(message: Message, state: FSMContext):
    city = message.text
    data = await get_weather(city, wether_api)

    if data == None:
        await message.answer("Такой город не найден, введите город ещё раз")
        return

    await db.add_user_city(message.from_user.id, city)
    string = await get_weather_day(data)

    await message.answer(string)
    await state.clear()

@router.message(F.text == "/three_days")
async def three_days_ask_city(message: Message, state: FSMContext) -> None:
    city = await db.get_user_city(message.from_user.id)
    if city != None:
        data = await get_weather(city, wether_api)
        string = await get_weather_three_day(data)

        await message.answer(string)
        await state.clear()

        return

    await message.answer("Введите название города")
    await state.set_state(Form.waiting_from_city_three_day)

@router.message(Form.waiting_from_city_three_day)
async def three_days(message: Message, state: FSMContext):
    city = message.text
    data = await get_weather(city, wether_api)

    if data == None:
        await message.answer("Такой город не найден, введите город ещё раз")
        return

    string = await get_weather_three_day(data)

    await message.answer(string)
    await state.clear()

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

@router.message(CommandStart)
async def command_start(message: Message) -> None:
    await message.answer(f"Привет, {message.from_user.full_name}" +
    """Вот список команд:
/new - Погода в данный момент
/day - Погода на день
/three_days - Погода на три дня""")

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