import asyncio

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc.constants import cancel_text
from tgbot.misc.i18n import _


def main_back_button():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="main_back")
        ]
    ])
    return keyboard


def main_user_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🛒 Каталог", switch_inline_query_current_chat=''),
            InlineKeyboardButton(text=_("💎 Ежедневный бонус"), callback_data="bonus")],
            [InlineKeyboardButton(text=_("🌐 Профиль"), callback_data="profile")],
            [InlineKeyboardButton(text=_("👄 Изменить язык"), callback_data="language")]
        ]
    )

    return keyboard


def main_admin_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🛒 Каталог", switch_inline_query_current_chat=''),
            InlineKeyboardButton(text=_("💎 Ежедневный бонус"), callback_data="bonus")],
            [InlineKeyboardButton(text=_("🌐 Профиль"), callback_data="profile")],
            [InlineKeyboardButton(text=_("👄 Изменить язык"), callback_data="language")],
            [InlineKeyboardButton(text=_("🔐 Административная панель"), callback_data="admin_panel")]
        ]
    )

    return keyboard


def admin_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            types.InlineKeyboardButton(text=_("🎁 Добавить товар"), callback_data="new_item"),
            types.InlineKeyboardButton(text=_("🔧 Редактирование или Удаление"), callback_data="change_item")],
            [types.InlineKeyboardButton(text=_("🔊 Рассылка"), callback_data="broadcast")],
            [types.InlineKeyboardButton(text=_("🗂 Главное меню"), callback_data="main_menu")]

        ]
    )

    return keyboard


async def get_item(message: types.Message, state):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=_("✅ Подтвердить"), callback_data="accept"),
            InlineKeyboardButton(text=_(cancel_text), callback_data="reject")]
        ])

    data = await state.get_data()

    title = data['title']
    description = data['description']
    price = data['price']
    photo_link = data['photo_link']

    text = _("Информация которую указали:\n\nНаименование товара: {title}\nОписание товара: {description}\n"
             "Цена товара: {price}\nДобавить товар?").format(title=title, description=description, price=price)

    await message.answer_photo(
        photo=photo_link,
        caption=text, reply_markup=keyboard)

    await asyncio.sleep(0.3)


def item_back():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")
        ]
    ])
    return keyboard


def cancel_item():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_(cancel_text), callback_data="item_cancel")
        ]
    ])

    return keyboard
