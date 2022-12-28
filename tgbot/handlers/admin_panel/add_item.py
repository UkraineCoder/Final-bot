import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.infrastucture.database.functions.item_func import add_new_item
from tgbot.infrastucture.telegraph.abstract import FileUploader
from tgbot.keyboards.inline.main_buttons import cancel_item, item_back, get_item
from tgbot.misc.delete_markup import delete_markup
from tgbot.misc.states import NewItem
from tgbot.misc.i18n import _


async def new_item(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await call.message.edit_text(_("✏️ Укажите название товара"), reply_markup=cancel_item())
    await state.update_data(msg=call.message.message_id)
    await NewItem.Title.set()


async def title(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("✏️ Укажите описание товара"), reply_markup=cancel_item())

    await state.update_data(title=message.text, msg=msg.message_id)
    await NewItem.Description.set()


async def title_validation(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n✏️ Вы ввели слишком много текста"), reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


async def description(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("✏️ Укажите стоимость товара.\nБез пробелов и других символов"), reply_markup=cancel_item())

    await state.update_data(description=message.text, msg=msg.message_id)
    await NewItem.Price.set()


async def description_validation(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n✏️ Вы ввели слишком много текста"), reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


async def validation_title_description(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n✏️ Укажите только текст"), reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


async def price(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("✏️ Укажите количество товара\n"), reply_markup=cancel_item())

    await state.update_data(price=int(message.text), msg=msg.message_id)
    await NewItem.Quantity.set()


async def quantity(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("🏞 Отправьте фотографию товара"), reply_markup=cancel_item())

    await state.update_data(quantity=int(message.text), msg=msg.message_id)
    await NewItem.Photo.set()


async def validation_price_quantity(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n🔖 Укажите только цифры, без пробелов и других символов.\n"
                                 "Также цифр не должно быть слишком много."), reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


async def photo(message: types.Message, state: FSMContext, file_uploader: FileUploader):
    await delete_markup(message, state)
    photo = message.photo[-1]

    await message.bot.send_chat_action(message.chat.id, 'upload_photo')
    uploaded_photo = await file_uploader.upload_photo(photo)

    await state.update_data(photo_link=uploaded_photo.link)
    await get_item(message, state)
    await NewItem.Finish.set()


async def photo_validation(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n🏞 Пришлите фото"), reply_markup=cancel_item())
    await state.update_data(msg=msg.message_id)


async def accept_item(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await call.answer()

    data = await state.get_data()

    title = data['title']
    description = data['description']
    price = data['price']
    quantity = data['quantity']
    photo_link = data['photo_link']

    await add_new_item(session, title=title, description=description, price=price, quantity=quantity, photo_link=photo_link)

    await call.message.delete()

    await call.message.answer(_("🎉 Вы создали товар"), reply_markup=item_back())

    await state.finish()


async def reject_item(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await call.message.answer(_('❌ Вы отменили создание товара'))
    await call.message.delete()
    await state.finish()


async def item_cancel(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await call.message.edit_text(_("❌ Вы отменили создание товара"), reply_markup=item_back())
    await state.finish()


def register_add_item(dp: Dispatcher):
    dp.register_callback_query_handler(item_cancel, text="item_cancel", state="*")
    dp.register_callback_query_handler(new_item, text="new_item")
    dp.register_message_handler(title, regexp=re.compile(r'^.{1,50}$'), state=NewItem.Title)
    dp.register_message_handler(title_validation, state=NewItem.Title)
    dp.register_message_handler(description, regexp=re.compile(r'^.{1,800}$'), state=NewItem.Description)
    dp.register_message_handler(description_validation, state=NewItem.Description)

    dp.register_message_handler(validation_title_description, state=[NewItem.Title, NewItem.Description], content_types=['any'])

    dp.register_message_handler(price, regexp=re.compile(r'^[0-9]{1,5}$'), state=NewItem.Price)
    dp.register_message_handler(quantity, regexp=re.compile(r'^[0-9]{1,5}$'), state=NewItem.Quantity)

    dp.register_message_handler(validation_price_quantity, state=[NewItem.Price, NewItem.Quantity], content_types=['any'])

    dp.register_message_handler(photo, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
    dp.register_message_handler(photo_validation, state=NewItem.Photo, content_types=['any'])

    dp.register_callback_query_handler(accept_item, text="accept", state=NewItem.Finish)
    dp.register_callback_query_handler(reject_item, text="reject", state=NewItem.Finish)


