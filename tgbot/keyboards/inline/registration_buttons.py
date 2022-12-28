from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.misc.i18n import _


def registration():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_("🔑 Код приглашения"), callback_data="invitation_code"),
             InlineKeyboardButton(text=_("✅ Подпишитесь на наш канал"), callback_data="subscribe_channel")]
        ]
    )
    return keyboard


def check_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=_("🔄 Проверить подписку"), callback_data="check_subs")
        ]]
    )

    return keyboard


def invitation_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="◀️ Назад", callback_data="invitation_back")
        ]]
    )

    return keyboard
