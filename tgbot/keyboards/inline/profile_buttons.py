from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.misc.i18n import _


def profile_ref():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=_("Мой рефер"), callback_data="profile_referrer"),
            InlineKeyboardButton(text=_("Мои рефералы"), callback_data="profile_referrals")]
        ]
    )

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_back"))

    return keyboard


def profile_ref_back():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="⬅️ Назад", callback_data="profile")]
        ]
    )

    return keyboard
