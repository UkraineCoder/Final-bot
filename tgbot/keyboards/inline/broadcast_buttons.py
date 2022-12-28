from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc.constants import cancel_text
from tgbot.misc.i18n import _


def broadcast_button():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("🗞 Отравить сейчас"),
                                 callback_data="broadcast_now"),
            InlineKeyboardButton(text=_("⏰ Запланировать отправку"),
                                 callback_data="broadcast_time")
        ],
        [InlineKeyboardButton(text=_(cancel_text), callback_data="admin_panel_cancel")]
    ])

    return keyboard


def cancel_news():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_(cancel_text), callback_data="admin_panel_cancel")
        ]
    ])

    return keyboard
