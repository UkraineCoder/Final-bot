from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hide_link

from tgbot.infrastucture.database.functions.item_func import item_all, item_all_like, get_count_item
from tgbot.misc.i18n import _


async def get_item(item_show_all, query):
    bot_user = await query.bot.me

    items = [types.InlineQueryResultArticle(
        id=item.id,
        title=item.title,
        description=str(item.price) + " грн",
        thumb_url=item.photo_link,
        input_message_content=types.InputTextMessageContent(message_text=_("📌 Название: {title}\n"
                                                                           "📝 Описание: {description}\n"
                                                                           "💰 Цена: {price}\n"
                                                                           "{photo_link}")
        .format(title=item.title, description=item.description, price=item.price,
                photo_link=hide_link(item.photo_link))),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=_("🛍 Показать товар"),
                                     url=f'https://t.me/{bot_user.username}?start=id_{item.id}')
            ]
        ]),
    ) for item in item_show_all if item.quantity != 0]

    return items


async def catalog(query: types.InlineQuery, session):
    count_item = await get_count_item(session)
    item_show_all = await item_all(session)
    check = sum(item_check.quantity for item_check in item_show_all)

    if count_item == 0 or check == 0:
        await query.bot.send_message(query.from_user.id, _("Все товары закончились"))
        return

    text = query.query
    text_len = len(text)

    if text_len < 2:
        item = await get_item(item_show_all, query)
    else:
        item_show_all_like = await item_all_like(session, text)

        item = await get_item(item_show_all_like, query)

    await query.answer(item, cache_time=1, is_personal=True)


def register_inline(dp: Dispatcher):
    dp.register_inline_handler(catalog)
