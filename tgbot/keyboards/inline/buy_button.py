from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.misc.constants import cancel_text
from tgbot.misc.i18n import _

buy_product = CallbackData("buy", "id", "quantity")
buy_balance = CallbackData("balance", "id", "quantity", "msg")
buy_card = CallbackData("card", "id", "quantity", "msg")


def buy_item(id, quantity):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=_("🛒 Купить товар"), callback_data=buy_product.new(id, quantity))
            ]
        ])

    return keyboard


def payment_menu(id, quantity, msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=_("💰 Оплата Балансом"), callback_data=buy_balance.new(id, quantity, msg)),
                InlineKeyboardButton(text=_("💳 Оплата Картой"), callback_data=buy_card.new(id, quantity, msg))
            ],
        [
            InlineKeyboardButton(text=_(cancel_text), callback_data="cancel"),
        ]
        ])

    return keyboard


def buy_cancel():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=_(cancel_text), callback_data="cancel")
            ]
        ])

    return keyboard