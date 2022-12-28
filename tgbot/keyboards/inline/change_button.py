from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from tgbot.misc.i18n import _

pagination_call = CallbackData("paginator", "key", "page", "item_id")
edit_call = CallbackData("edit", "id", "characteristics")


def get_page_keyboard(max_pages: int, id: int, key="item", page: int = 1):
    previous_page = page - 1
    previous_page_text = "<< "

    current_page_text_edit = _("⚒ Редактировать")
    current_page_text_delete = _(f"❌ Удалить")

    next_page = page + 1
    next_page_text = " >>"

    markup = InlineKeyboardMarkup().row()
    if previous_page > 0:
        markup.insert(
            InlineKeyboardButton(
                text=previous_page_text,
                callback_data=pagination_call.new(key=key, page=previous_page, item_id=id)
            )
        )

    markup.insert(
        InlineKeyboardButton(
            text=current_page_text_edit,
            callback_data=pagination_call.new(key=key, page="current_page_edit", item_id=id)
        )
    )

    markup.insert(
        InlineKeyboardButton(
            text=current_page_text_delete,
            callback_data=pagination_call.new(key=key, page="current_page_delete", item_id=id)
        )
    )

    if next_page < max_pages:
        markup.insert(
            InlineKeyboardButton(
                text=next_page_text,
                callback_data=pagination_call.new(key=key, page=next_page, item_id=id)
            )
        )

    markup.add(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data="admin_panel"
        )
    )

    return markup


def edit_item_button(item_id: int, characteristics: str = "title"):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_("📌 Название"), callback_data=edit_call.new(id=item_id, characteristics=characteristics)),
             InlineKeyboardButton(text=_("📝 Описание"), callback_data=edit_call.new(id=item_id, characteristics="description"))],
            [InlineKeyboardButton(text=_("🏞 Фотография"), callback_data=edit_call.new(id=item_id, characteristics="photo_link")),
             InlineKeyboardButton(text=_("💎 Количество"), callback_data=edit_call.new(id=item_id, characteristics="quantity")),
             InlineKeyboardButton(text=_("💰 Цена"), callback_data=edit_call.new(id=item_id, characteristics="price"))],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="change_item")]
        ])

    return keyboard


def delete_item_button(max_pages):
    if max_pages > 1:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="change_item")]
            ])
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_panel")]
            ])

    return keyboard
