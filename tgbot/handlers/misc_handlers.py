from aiogram import Dispatcher, types

from tgbot.config import load_config
from tgbot.keyboards.inline.main_buttons import main_admin_button, main_user_button
from tgbot.misc.i18n import _


async def echo_start(message: types.Message):
    if message.reply_markup or message.content_type == "successful_payment":
        return

    await message.answer(_("Нажмите на команду /start"))


async def main_menu(call):
    config = load_config(".env")

    if call.from_user.id in config.tg_bot.admin_ids:
        await call.message.edit_text(_("🗂 Главное меню"), reply_markup=main_admin_button())
    else:
        await call.message.edit_text(_("🗂 Главное меню"), reply_markup=main_user_button())

    # await call.message.edit_reply_markup(reply_markup=None)


def register_misc(dp: Dispatcher):
    dp.register_callback_query_handler(main_menu, text="main_back", state="*")
    dp.register_message_handler(echo_start, content_types=types.ContentType.ANY)
