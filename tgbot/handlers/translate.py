from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from tgbot.infrastucture.database.functions.users import update_user
from tgbot.infrastucture.database.models.users import User


async def change_language(call: CallbackQuery, user: User, session):
    if user.language == 'ru':
        await update_user(session, User.telegram_id == call.from_user.id, language='uk')
        await call.answer("Мова була змінена\n"
                          "Натисніть /start щоб побачити зміни", show_alert=True)
    else:
        await update_user(session, User.telegram_id == call.from_user.id, language='ru')
        await call.answer("Язык был изменен!\n"
                          "Нажмите /start чтобы увидеть изменения", show_alert=True)


def register_language(dp: Dispatcher):
    dp.register_callback_query_handler(change_language, text="language", state="*")
