import config
import logging
import asyncio
from datetime import datetime
from pokemon import Pokemon
from aiogram import types
import wikipedia
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from sqlighter import SQLighter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

wikipedia.set_lang("ru")

# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

# инициализируем соединение с БД
db = SQLighter('db.db')


@dp.message_handler(commands=['post'])
async def post(message: types.Message):
    config.PHOTO = True
    await message.answer('Отправьте post ->')


@dp.message_handler(commands=['getpost'])
async def getphoto(message: types.Message):
    with open("photos.txt", "r") as f:
        content = f.readlines()
        f.close()

    await message.answer(f'Post: {content}')


@dp.message_handler(commands=['start'])
async def subscribe(message: types.Message):
    await message.answer(
        "Добро пожаловать! Этот бот поможет вам найти характерискити покемона.\nЧтобы посмотреть характеристики "
        "необходимо подписаться.")


# Команда активации подписки
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, True)

    await message.answer("Успешный успех :3")


# Команда отписки
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")


@dp.message_handler(commands=['pokemon'])
async def pokemon(message: types.Message):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    result = cur.execute("""SELECT status FROM subscriptions""").fetchall()
    if result[0][0]:
        config.FLAG = True
        await message.answer("Введите имя покемона с маленькой буквы ->")
    else:
        await message.answer("Необходима подписка")


@dp.message_handler(commands=['wiki'])
async def wiki(message: types.Message):
    config.WIKI = True
    await message.answer('Введите что хотите')


@dp.message_handler()
async def check(message: types.Message):
    if config.WIKI:
        result = wikipedia.summary(message.text, sentences=2)
        await message.answer(result)
        config.WIKI = False
    if config.PHOTO:
        with open('photos.txt', 'w+') as f:
            f.write(message.text)
            f.close()

            inline_btn = InlineKeyboardButton('post', callback_data="get_link_button")
            inline_kb = InlineKeyboardMarkup().add(inline_btn)
        config.PHOTO = False
        await message.bot.send_message(config.CHANEL_ID, message.text, reply_markup=inline_kb)
        await message.answer('OK')

    if db.subscriber_exists(message.from_user.id) and config.FLAG:
        poke = message.text
        await message.answer(f"Имя покемона: {Pokemon(poke).name()}\nНомер: {Pokemon(poke).order()}\n"
                             f"Способности: {Pokemon(poke).abilities()}\nРост: {Pokemon(poke).height()} м\n"
                             f"Вес: {Pokemon(poke).weight()} кг")
        config.FLAG = False


# запускаем лонг поллинг
if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.create_task(scheduled(10))  # 10 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)
