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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from datetime import date, timedelta

from weather import get_weather, get_weather_new, get_weather_new_data, get_weather_day, get_weather_three_day, get_weather_three_days_data, get_weather_tomorow, get_weather_data, parse_custom_date, date_diff
from image import generate_weather_widget, generate_weather_widget_three_days, generate_weather_widget_hourly
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
    waiting_from_city_tomorow = State()

    menu_new = State()
    menu_three_days = State()

class DaySelectCallback(CallbackData, prefix="select_day"):
    day_offset: int


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
    city = message.text
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
    print("get_wether_day")
    await handle_weather_command(
        message=message,
        state=state,
        form_func=get_weather_day,
        next_state=Form.waiting_from_city_day
    )

@router.message(Form.waiting_from_city_day)
async def weather_day(message: Message, state: FSMContext):
    print("get_wether_day_callback")
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

async def link_start_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Сейчас", callback_data='menu_new')
    builder.button(text="Сегодня", callback_data= DaySelectCallback(day_offset = 0))
    builder.button(text="Завтра", callback_data= DaySelectCallback(day_offset = 1))
    builder.button(text="На 3 дня", callback_data= 'menu_three_days')
    builder.button(text="Выбрать дату", callback_data= 'enter_custom_date')

    builder.adjust(1, 2, 1, 1)
    return builder.as_markup()

async def link_castom_date_kb():
    builder = InlineKeyboardBuilder()
    todday = date.today()

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    for i in range(2,7):
        target_day = todday + timedelta(days=i)
        day_str = target_day.strftime("%d.%m")
        weekday_str = weekdays[target_day.weekday()]

        btn_text = f"{weekday_str}, {day_str}"

        builder.button(text=btn_text, callback_data=DaySelectCallback(day_offset = i))
    
    builder.adjust(2)
    return builder.as_markup()

async def link_castom_date_back_kb():
    builder = InlineKeyboardBuilder()

    builder.button(text="Выбрать дату", callback_data='enter_custom_date')
    builder.button(text="Назад", callback_data='enter_start')

    return builder.as_markup()

@router.callback_query(DaySelectCallback.filter())
async def procces_select_day(call: CallbackQuery, callback_data: DaySelectCallback):
    await call.answer()

    day = callback_data.day_offset

    city = await db.get_user_city(call.from_user.id)
    data = await get_weather(city, wether_api)

    time_list, temp_list, app_temp_list, weather_list, day_date_str = await get_weather_data(data, day)
    file_path = await generate_weather_widget_hourly(city, day_date_str, temp_list, app_temp_list, weather_list, call.from_user.id)

    image = FSInputFile(file_path)

    if day == 0 or day == 1:
        kb = await link_start_kb()
    else:
        kb = await link_castom_date_back_kb()
    
    await call.message.delete()
    await call.message.answer_photo(photo=image, caption=f"Выберите нужную опцию:", reply_markup=kb)

@router.callback_query(F.data == 'menu_new')
async def procces_weathre_new(call: CallbackQuery):
    await call.answer()

    kb = await link_start_kb()

    city = await db.get_user_city(call.from_user.id)
    data = await get_weather(city, wether_api)

    current_temp, app_current_temp, weather, day_date_str = await get_weather_new_data(data)

    file_path = await generate_weather_widget(city, day_date_str, current_temp, app_current_temp, weather, call.from_user.id)
    image = FSInputFile(file_path)

    await call.message.delete()

    await call.message.answer_photo(photo=image, caption="Выберите нужную опцию:", reply_markup=kb)

@router.callback_query(F.data == 'enter_custom_date')
async def procces_enter_select_custom_day(call: CallbackQuery):
    await call.answer()

    kb = await link_castom_date_kb()
    await call.message.delete()

    await call.message.answer("Выберете дату:", reply_markup = kb)

@router.callback_query(F.data == 'menu_three_days')
async def procces_three_days(call: CallbackQuery):
    await call.answer()

    kb = await link_start_kb()

    city = await db.get_user_city(call.from_user.id)
    data = await get_weather(city, wether_api)

    current_temp_list, app_current_temp_list, weather_list, third_day = await get_weather_three_days_data(data)

    file_path = await generate_weather_widget_three_days(city, current_temp_list, app_current_temp_list, weather_list, third_day, call.from_user.id)
    image = FSInputFile(file_path)
    await call.message.delete()

    await call.message.answer_photo(photo=image, caption=f"Погода на 3 дня в {city}", reply_markup=kb)

@router.callback_query(F.data == 'enter_start')
async def procces_weathre_new(call: CallbackQuery):
    await call.answer()

    kb = await link_start_kb()
    await call.message.delete()

    await call.message.answer(text="Выберите нужную опцию:", reply_markup = kb)

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
    
    kb = await link_start_kb()

    await db.add_user_city(message.from_user.id, city)
    await message.answer(f"Ваш город был изменен на <b>{city}</b> \nВыберете опцию:", reply_markup= kb)

    await state.clear()

@router.message(F.text == '/image')
async def create_image(message: Message):
    city = await db.get_user_city(message.from_user.id)
    data = await get_weather(city, wether_api)

    current_temp, app_current_temp, weather, day_date_str = await get_weather_new_data(data)

    file_path = await generate_weather_widget(city, day_date_str, current_temp, app_current_temp, weather, call.from_user.id)
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

@router.message(Command("image_select_day"))
async def create_image_select_day(message: Message, command: CommandObject):
    args = command.args
    if args == None:
        await message.answer(
            "Вы не ввели дату, после команды /image_select_day нужно писать дату (/image_select_day день) или (/image_select_day день.месяц)"
        )
        return
    try:
        city = await db.get_user_city(message.from_user.id)
        data = await get_weather(city, wether_api)

        select_day = (await parse_custom_date(str(args))).date()

        day_dif = await date_diff(select_day)

        if day_dif >= 7 or day_dif < 0:
            await message.answer("Нет данных на этот день")
            return
        
        time_list, temp_list, app_temp_list, weather_list, day_date_str = await get_weather_data(data, day_dif)
        file_path = await generate_weather_widget_hourly(city, day_date_str, temp_list, app_temp_list, weather_list, message.from_user.id)

        image = FSInputFile(file_path)

        await message.answer_photo(photo=image, caption=f"Погода в {city}")
        
    except ValueError:
        await message.answer("Некорректная дата")
    


@router.message(CommandStart)
async def command_start(message: Message, state: FSMContext) -> None:
    city = await db.get_user_city(message.from_user.id)
    has_city = city is not None

    if has_city:
        kb = await link_start_kb()
        text = f"Привет, {message.from_user.full_name}! Ваш город: <b>{city}</b>.\nВыберите нужную опцию:"
        await message.answer(text, reply_markup=kb)
    else:
        text = f"Привет, {message.from_user.full_name}! Чтобы пользоваться ботом, укажите ваш город."
        await state.set_state(Form.waiting_from_update_city)
        await message.answer(text)

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