"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
from auth_data import token
from work_calendar import add_work

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = token

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(commands=['add'])
async def send_welcome(message: types.Message):
    expense = add_work(message.text)
    await message.reply(f"Hi!\nI'm EchoBot!\n{expense}.")



@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)