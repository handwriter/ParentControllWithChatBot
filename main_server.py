from database import DB
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.utils import executor
from aiogram.utils.markdown import text, bold, italic, code, pre
from multiprocessing import Process
import asyncio
from server_flask_app import app

TOKEN = '6054188657:AAFuLQ7yyPUdhQmau7TGmsG776Ny5YTElZ4'


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def GenerateMainKeyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🖼 Получить скриншот"))
    return keyboard




@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    msg = await message.reply("Привет!\n 👋 Ты хочешь зарегестрироваться?")
    button_yes = InlineKeyboardButton('Да', callback_data=f"first_q|yes|{msg.message_id}")
    button_no = InlineKeyboardButton('Нет', callback_data=f"first_q|no|{msg.message_id}")

    greet_kb = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_yes, button_no)
    await msg.edit_reply_markup(reply_markup=greet_kb)

@dp.callback_query_handler(lambda d: d.data and d.data.startswith("first_q"))
async def first_quest(callback: types.CallbackQuery):

    if "yes" in callback.data:
        if DB.get_user_by_chat_id(callback.from_user.id) is None:
            DB.create_user(callback.from_user.id)
        txt = text("Отлично. Твой ID: ", code(f"{callback.from_user.id}"), "\nВведи его в приложении на устройстве")
        await bot.edit_message_text(txt, message_id=callback.data.split("|")[-1], chat_id=callback.from_user.id, parse_mode=ParseMode.MARKDOWN, reply_markup=GenerateMainKeyboard())
    else:
        await bot.edit_message_text("Хорошо, но ты можешь сделать это позднее, командой /start", message_id=callback.data.split("|")[-1], chat_id=callback.from_user.id)

@dp.message_handler(lambda x: "Получить скриншот" in x.text)
async def send_screenshot(message: types.Message):
    await message.reply("Cringe")


def bot_init():
    loop = asyncio.get_event_loop()
    loop.create_task(check_messages_to_send(1))
    executor.start_polling(dp)

async def check_messages_to_send(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        for nt in DB.get_notifies():
            await bot.send_message(nt[1], nt[2], parse_mode="HTML")
            DB.delete_notify_by_id(nt[0])


if __name__ == '__main__':

    Process(target=bot_init).start()
    app.run("0.0.0.0", 689, use_reloader=False)
    # Process(target=app.run, args=("127.0.0.1", "5000"))
    # loop = asyncio.get_event_loop()
    # loop.create_task(app.run)
    # executor.start_polling(dp)
    # asyncio.set_event_loop(asyncio.new_event_loop())
    # executor.start_polling(dp, skip_updates=True)