from aiogram import types
from dispatcher import dp
from dispatcher import bot
import config


@dp.callback_query_handler(lambda c: c.data == "get_link_button")
async def process_callback_get_link_button(c: types.CallbackQuery):
    try:
        member = await bot.get_chat_member(config.CHANEL_ID, c.from_user.id)

        if member["status"] in ("member", "creator", "administrator"):
            with open("photos.txt", "r") as f:
                content = f.readlines()
                f.close()
            await bot.answer_callback_query(c.id, f"Ссылка - {content[0].strip()}", show_alert=True)
        else:
            await bot.answer_callback_query(c.id, f"NO", show_alert=True)
    except:
        await bot.answer_callback_query(c.id, f"NO", show_alert=True)
