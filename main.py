import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging

MY_BOT_TOKEN = os.getenv('7286514059:AAGXDUwTBauLXgj2BvepNlNZkRoLmCcB4z8')

bot = Bot(token=MY_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    role = State()
    from_city = State()
    to_city = State()
    date = State()
    price = State()
    priority = State()

role_kb = ReplyKeyboardMarkup(resize_keyboard=True)
role_kb.add(KeyboardButton("Жүргүзүүчү"), KeyboardButton("Жолооучу"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Саламатсызбы! Сиз кимсиз?", reply_markup=role_kb)
    await Form.role.set()

@dp.message_handler(state=Form.role)
async def set_role(message: types.Message, state: FSMContext):
    await state.update_data(role=message.text)
    await message.answer("Кайсы шаардан чыгасыз?")
    await Form.next()

@dp.message_handler(state=Form.from_city)
async def set_from(message: types.Message, state: FSMContext):
    await state.update_data(from_city=message.text)
    await message.answer("Кайсы шаарга барасыз?")
    await Form.next()

@dp.message_handler(state=Form.to_city)
async def set_to(message: types.Message, state: FSMContext):
    await state.update_data(to_city=message.text)
    await message.answer("Качан жолго чыгасыз? (мисалы: 3-июнь, саат 10:00)")
    await Form.next()

@dp.message_handler(state=Form.date)
async def set_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer('Баасы канча? (же "жок")')
    await Form.next()

@dp.message_handler(state=Form.price)
async def set_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    priority_kb = InlineKeyboardMarkup()
    priority_kb.add(
        InlineKeyboardButton("Бекер жарыя", callback_data="free"),
        InlineKeyboardButton("Приоритеттүү жарыя (төлөм) 💰", callback_data="paid")
    )
    await message.answer("Жарыянын түрүн тандаңыз:", reply_markup=priority_kb)
    await Form.next()

@dp.callback_query_handler(lambda c: c.data in ['free', 'paid'], state=Form.priority)
async def set_priority(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    priority = call.data
    await call.message.delete()

    text = (f"🚘 {data['role']} из {data['from_city']} в {data['to_city']}\n"
            f"📅 {data['date']}\n"
            f"💸 {data['price']}\n"
            f"👤 {call.from_user.mention}")

    if priority == 'paid':
        text = "💰 *ПРИОРИТЕТТҮҮ ЖАРЫЯ!*\n" + text
        await call.message.answer("Админ менен байланышып, төлөм жасаңыз: @admin_username")

    await bot.send_message(chat_id='@poputchik_kyrgyzstan', text=text, parse_mode="Markdown")
    await call.message.answer("Жарыя жөнөтүлдү. Рахмат! ✅")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
