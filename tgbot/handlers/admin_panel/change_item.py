import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hide_link
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastucture.database.functions.item_func import item_all, get_count_item, update_item, delete_item, \
    get_one_item
from tgbot.infrastucture.database.models.item import Item
from tgbot.infrastucture.telegraph.abstract import FileUploader
from tgbot.keyboards.inline.change_button import get_page_keyboard, pagination_call, \
    edit_item_button, edit_call, delete_item_button
from tgbot.keyboards.inline.main_buttons import cancel_item
from tgbot.misc.delete_markup import delete_markup
from tgbot.misc.states import EditItem
from tgbot.misc.i18n import _


def get_page(array, page: int = 1):
    page_index = page - 1
    return array[page_index]


async def current_page_edit(call: CallbackQuery, callback_data: dict, session):
    item_id = int(callback_data.get("item_id"))

    item_show_all = await item_all(session)

    if item_show_all:
        await call.answer()
        await call.message.edit_text(_("📝 Что вы хотите редактировать?"),
                                     reply_markup=edit_item_button(item_id=item_id))
    else:
        await call.answer(_("Добавьте хотя бы один товар!"), show_alert=True)


async def current_page_delete(call: CallbackQuery, callback_data: dict, session):
    item_id = int(callback_data.get("item_id"))
    item = await get_one_item(session, id=item_id)

    if item:
        await call.answer()
        await delete_item(session, Item.id == item_id)
        max_pages = await get_count_item(session) + 1
        await call.message.edit_text(_("✅ Запись удалена"), reply_markup=delete_item_button(max_pages))
    else:
        await call.answer(_("Кажется товар был удален"), show_alert=True)


async def pages(call, item_show_all, current_page, max_pages):
    await call.answer()

    page = get_page(item_show_all, page=current_page)
    text = _("📫 Артикл: {id}\n📌 Название: {title}\n💎 Количество: {quantity}\n "
             "📝 Описание: {description}\n💰 Цена: {price}\n{photo_link}") \
        .format(id=page.id, title=page.title, quantity=page.quantity, description=page.description, price=page.price,
                photo_link=hide_link(page.photo_link))

    markup = get_page_keyboard(max_pages=max_pages, id=page.id, page=current_page)
    await call.message.edit_text(text=text, reply_markup=markup)


async def page(call, item_show_all, session):
    await call.answer()

    page = get_page(item_show_all)
    text = _("📫 Артикл: {id}\n📌 Название: {title}\n💎 Количество: {quantity}\n "
             "📝 Описание: {description}\n💰 Цена: {price}\n{photo_link}") \
        .format(id=page.id, title=page.title, quantity=page.quantity, description=page.description, price=page.price,
                photo_link=hide_link(page.photo_link))

    max_pages = await get_count_item(session) + 1
    await call.message.edit_text(text,
                                 reply_markup=get_page_keyboard(max_pages=max_pages, id=page.id))


async def item_pages(call: CallbackQuery, callback_data: dict, session):
    item_show_all = await item_all(session)
    max_pages = await get_count_item(session) + 1
    current_page = int(callback_data.get("page"))

    if max_pages == 1:
        return await call.answer(_("Добавьте хотя бы один товар!"), show_alert=True)

    try:
        await pages(call, item_show_all, current_page, max_pages)
    except Exception:
        item_show_all_now = await item_all(session)
        max_pages_now = await get_count_item(session) + 1

        if max_pages_now <= 2:
            await page(call, item_show_all_now, session)
        else:
            current_page_now = int(callback_data.get("page"))
            await pages(call, item_show_all, current_page_now, max_pages_now)


async def item_page(call: CallbackQuery, session):
    item_show_all = await item_all(session)
    if item_show_all:
        await page(call, item_show_all, session)
    else:
        await call.answer(_("Добавьте хотя бы один товар!"), show_alert=True)


async def title(call: CallbackQuery, callback_data: dict, state: FSMContext, session):
    item_id = int(callback_data.get("id"))

    item = await get_one_item(session, id=item_id)

    if item:
        await call.answer()

        await call.message.edit_text(_("✏️ Укажите название товара"), reply_markup=cancel_item())
        await state.update_data(msg=call.message.message_id, item_id=item_id)
        await EditItem.Title.set()
    else:
        await call.answer(_("Кажется товар был удален"), show_alert=True)


async def edit_title(message: Message, session, state: FSMContext):
    await delete_markup(message, state)
    data = await state.get_data()

    item_id = data['item_id']

    await message.answer(_("✅ Название было изменено"), reply_markup=edit_item_button(item_id=item_id))
    await update_item(session, Item.id == item_id, title=message.text)
    await state.finish()


async def edit_title_validation(message: Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n✏️ Вы ввели слишком много текста"), reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


async def description(call: CallbackQuery, callback_data: dict, state: FSMContext, session):
    item_id = int(callback_data.get("id"))

    item = await get_one_item(session, id=item_id)

    if item:
        await call.answer()

        await call.message.edit_text(_("✏️ Укажите описание товара"), reply_markup=cancel_item())
        await state.update_data(msg=call.message.message_id, item_id=item_id)
        await EditItem.Description.set()
    else:
        await call.answer(_("Кажется товар был удален"), show_alert=True)


async def edit_description(message: Message, session, state: FSMContext):
    await delete_markup(message, state)
    data = await state.get_data()

    item_id = data['item_id']

    await message.answer(_("✅ Описание было изменено"), reply_markup=edit_item_button(item_id=item_id))
    await update_item(session, Item.id == item_id, description=message.text)
    await state.finish()


async def edit_description_validation(message: Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n✏️ Вы ввели слишком много текста"), reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


async def edit_validation_title_description(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n✏️ Укажите только текст"), reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


async def price(call: CallbackQuery, callback_data: dict, state: FSMContext, session):
    item_id = int(callback_data.get("id"))

    item = await get_one_item(session, id=item_id)

    if item:
        await call.answer()

        await call.message.edit_text(_("✏️ Укажите цену товара"), reply_markup=cancel_item())
        await state.update_data(msg=call.message.message_id, item_id=item_id)
        await EditItem.Price.set()
    else:
        await call.answer(_("Кажется товар был удален"), show_alert=True)


async def edit_price(message: Message, session, state: FSMContext):
    await delete_markup(message, state)
    data = await state.get_data()

    item_id = data['item_id']

    await message.answer(_("✅ Цену было изменено"), reply_markup=edit_item_button(item_id=item_id))
    await update_item(session, Item.id == item_id, price=int(message.text))
    await state.finish()


async def quantity(call: CallbackQuery, callback_data: dict, state: FSMContext, session):
    item_id = int(callback_data.get("id"))

    item = await get_one_item(session, id=item_id)

    if item:
        await call.answer()

        await call.message.edit_text(_("✏️ Укажите количество товара"), reply_markup=cancel_item())
        await state.update_data(msg=call.message.message_id, item_id=item_id)
        await EditItem.Quantity.set()
    else:
        await call.answer(_("Кажется товар был удален"), show_alert=True)


async def edit_quantity(message: Message, session, state: FSMContext):
    await delete_markup(message, state)
    data = await state.get_data()

    item_id = data['item_id']

    await message.answer(_("✅ Количество было изменено"), reply_markup=edit_item_button(item_id=item_id))
    await update_item(session, Item.id == item_id, quantity=int(message.text))
    await state.finish()


async def edit_validation_price_quantity(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n🔖 Укажите только цифры, без пробелов и других символов\n"
                                 "Также цифр не должно быть слишком много."),
                               reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


async def photo(call: CallbackQuery, callback_data: dict, state: FSMContext, session):
    item_id = int(callback_data.get("id"))

    item = await get_one_item(session, id=item_id)

    if item:
        await call.answer()

        await call.message.edit_text(_("🏞 Отправьте фотографию товара"), reply_markup=cancel_item())
        await state.update_data(msg=call.message.message_id, item_id=item_id)
        await EditItem.Photo.set()
    else:
        await call.answer(_("Кажется товар был удален"), show_alert=True)


async def edit_photo(message: Message, state: FSMContext, file_uploader: FileUploader, session: AsyncSession):
    await delete_markup(message, state)
    data = await state.get_data()

    item_id = data['item_id']
    photo = message.photo[-1]

    await message.bot.send_chat_action(message.chat.id, 'upload_photo')
    uploaded_photo = await file_uploader.upload_photo(photo)

    await message.answer(_("✅ Фото было изменено"), reply_markup=edit_item_button(item_id=item_id))
    await update_item(session, Item.id == item_id, photo_link=uploaded_photo.link)
    await state.finish()


async def edit_photo_validation(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n🏞 Пришлите фото"), reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


def register_change_item(dp: Dispatcher):
    dp.register_callback_query_handler(title, edit_call.filter(characteristics="title"))
    dp.register_message_handler(edit_title, regexp=re.compile(r'^.{1,50}$'), state=EditItem.Title)
    dp.register_message_handler(edit_title_validation, state=EditItem.Title)

    dp.register_callback_query_handler(description, edit_call.filter(characteristics="description"))
    dp.register_message_handler(edit_description, regexp=re.compile(r'^.{1,800}$'), state=EditItem.Description)
    dp.register_message_handler(edit_description_validation, state=EditItem.Description)

    dp.register_message_handler(edit_validation_title_description, state=[EditItem.Title, EditItem.Description],
                                content_types=['any'])

    dp.register_callback_query_handler(price, edit_call.filter(characteristics="price"))
    dp.register_message_handler(edit_price, regexp=re.compile(r'^[0-9]{1,5}$'), state=EditItem.Price)

    dp.register_callback_query_handler(quantity, edit_call.filter(characteristics="quantity"))
    dp.register_message_handler(edit_quantity, regexp=re.compile(r'^[0-9]{1,5}$'), state=EditItem.Quantity)

    dp.register_message_handler(edit_validation_price_quantity, state=[EditItem.Price, EditItem.Quantity],
                                content_types=['any'])

    dp.register_callback_query_handler(photo, edit_call.filter(characteristics="photo_link"))
    dp.register_message_handler(edit_photo, state=EditItem.Photo, content_types=types.ContentType.PHOTO)
    dp.register_message_handler(edit_photo_validation, state=EditItem.Photo, content_types=['any'])

    dp.register_callback_query_handler(current_page_edit, pagination_call.filter(page="current_page_edit"))
    dp.register_callback_query_handler(current_page_delete, pagination_call.filter(page="current_page_delete"))
    dp.register_callback_query_handler(item_pages, pagination_call.filter(key="item"))
    dp.register_callback_query_handler(item_page, text="change_item")
