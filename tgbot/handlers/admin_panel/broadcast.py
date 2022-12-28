import asyncio
import datetime
import re

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import BotBlocked
from sqlalchemy.orm import sessionmaker

from tgbot.filters.time import HourFilter, MinuteFilter
from tgbot.handlers.aiogram_calendar.simple_calendar import calendar_callback, SimpleCalendar
from tgbot.infrastucture.database.functions.users import get_user_id
from tgbot.keyboards.inline.broadcast_buttons import cancel_news, broadcast_button
from tgbot.keyboards.inline.main_buttons import admin_keyboard
from tgbot.misc.constants import channels
from tgbot.misc.delete_markup import delete_markup
from tgbot.misc.states import Broadcast
from tgbot.misc.i18n import _


async def broadcast_news(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await call.message.edit_text(_("✏️ Укажите название статьи"), reply_markup=cancel_news())
    await state.update_data(msg=call.message.message_id)
    await Broadcast.Title.set()


async def broadcast_title(message: types.Message, state: FSMContext):
    await delete_markup(message, state)

    msg = await message.answer(_("✏️ Укажите описание статьи"), reply_markup=cancel_news())

    await state.update_data(title=message.text, msg=msg.message_id)
    await Broadcast.Description.set()


async def broadcast_title_validation(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n✏️ Вы ввели слишком много текста"), reply_markup=cancel_news())
    await state.update_data(msg=msg.message_id)


async def broadcast_description(message: types.Message, state: FSMContext):
    await delete_markup(message, state)

    msg = await message.answer(_("🏞 Отправьте фото"), reply_markup=cancel_news())

    await state.update_data(description=message.text, msg=msg.message_id)
    await Broadcast.Photo.set()


async def broadcast_description_validation(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n✏️ Вы ввели слишком много текста"), reply_markup=cancel_news())
    await state.update_data(msg=msg.message_id)


async def validation_title_description(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n✏️ Укажите только текст"), reply_markup=cancel_news())
    await state.update_data(msg=msg.message_id)


async def broadcast_photo(message: types.Message, state: FSMContext):
    await delete_markup(message, state)

    photo = message.photo[-1].file_id

    await message.bot.send_chat_action(message.chat.id, 'upload_photo')

    await message.answer(_("📰 Новость создана!\nВы хотите отправить её сейчас или запланировать отправку?"),
                         reply_markup=broadcast_button())

    await state.update_data(photo=photo)
    await Broadcast.Choose_Sending.set()


async def validation_photo(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка\n🏞 Пришлите фото"), reply_markup=cancel_news())
    await state.update_data(msg=msg.message_id)


async def broadcast_admin_panel(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(_("🎛 Административная панель"), reply_markup=admin_keyboard())
    await state.finish()


async def broadcast_text(message: types.Message):
    await message.answer(_("❗️ Выберите нужную кнопку!"))


async def broadcast_send_now(call: CallbackQuery, session, state: FSMContext):
    await call.answer()

    data = await state.get_data()

    title = data['title']
    description = data['description']
    photo = data['photo']

    text = f"{title}\n\n" \
           f"{description}"

    for user_id in list(await get_user_id(session)):
        try:
            if user_id == int(channels[0]):
                pass
            else:
                await call.bot.send_photo(chat_id=user_id, photo=photo, caption=text)
        except BotBlocked:
            pass

    await asyncio.sleep(0.02)

    await call.message.edit_text(_("✅ Рассылка выполнена!"), reply_markup=admin_keyboard())
    await state.finish()


async def broadcast_send_time(call: CallbackQuery):
    await call.answer()

    await call.message.edit_text(_("🗓 Пожалуйста выберите дату"), reply_markup=await SimpleCalendar().start_calendar())

    await Broadcast.Choose_Calendar.set()


async def broadcast_calendar_true(call, state, date_calendar):
    await call.message.edit_text(_("⏰ В сколько часов нужно отправить новость?"), reply_markup=cancel_news())

    await state.update_data(date=str(date_calendar), msg=call.message.message_id)

    await Broadcast.Choose_Hour.set()


async def broadcast_calendar(call: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date_calendar = await SimpleCalendar().process_selection(call, callback_data)
    if selected:
        date = str(date_calendar).split()[0]
        date_now = str(datetime.datetime.now()).split()[0]

        my_dt = datetime.datetime.strptime(str(date), '%Y-%m-%d')
        date_now_sort = datetime.datetime.strptime(str(date_now), '%Y-%m-%d')

        if my_dt == date_now_sort:
            await broadcast_calendar_true(call, state, date_calendar)
        elif my_dt >= datetime.datetime.now():
            await broadcast_calendar_true(call, state, date_calendar)
        else:
            await call.answer(_("❗️ Вы не можете отправить новость в прошлое"), show_alert=True)


async def broadcast_calendar_text(message: types.Message):
    await message.answer(_("❗️ Выберите дату отправки!"))


async def broadcast_calendar_hour(message: types.Message, state: FSMContext):
    await delete_markup(message, state)

    msg = await message.answer(_("⏰ В сколько минут нужно отправить новость?"), reply_markup=cancel_news())

    await state.update_data(hour=message.text, msg=msg.message_id)

    await Broadcast.Choose_Minute.set()


async def broadcast_calendar_hour_validation(message: types.Message, state: FSMContext):
    await delete_markup(message, state)

    msg = await message.answer(_("❌ Ошибка\n"
                               "Отправьте число от 0-23 и без лишних символов"), reply_markup=cancel_news())

    await state.update_data(msg=msg.message_id)


async def broadcast_job(photo, text: str, bot: Bot, session_pool: sessionmaker):
    async with session_pool() as session:
        for user_id in list(await get_user_id(session)):
            try:
                if user_id == int(channels[0]):
                    pass
                else:
                    await bot.send_photo(chat_id=user_id, photo=photo, caption=text)
            except BotBlocked:
                pass

        await asyncio.sleep(0.02)


async def broadcast_calendar_minute(message: types.Message, state: FSMContext, scheduler):
    await delete_markup(message, state)

    data = await state.get_data()

    title = data['title']
    description = data['description']
    photo = data['photo']
    date = data['date'].split()
    hour = data['hour']
    minute = message.text

    date_sort = date[0].split("-")
    year = int(date_sort[0])
    month = int(date_sort[1])
    day = int(date_sort[2])

    text = f"{title}\n\n" \
           f"{description}"

    scheduler.add_job(
        broadcast_job,
        'date',
        run_date=datetime.datetime(year=year, month=month, day=day, hour=int(hour), minute=int(minute)),
        timezone='Europe/Kiev',
        kwargs=dict(photo=photo, text=text)
    )

    await message.answer(_("✅ Рассылка запланирована!"), reply_markup=admin_keyboard())
    await state.finish()


async def broadcast_calendar_minute_validation(message: types.Message, state: FSMContext):
    await delete_markup(message, state)

    msg = await message.answer(_("❌ Ошибка\n"
                               "Отправьте число от 0-59 и без лишних символов"), reply_markup=cancel_news())

    await state.update_data(msg=msg.message_id)


def register_broadcast(dp: Dispatcher):
    dp.register_callback_query_handler(broadcast_admin_panel, text="admin_panel_cancel",
                                       state="*")

    dp.register_callback_query_handler(broadcast_news, text="broadcast")
    dp.register_message_handler(broadcast_title, regexp=re.compile(r'^.{1,50}$'), state=Broadcast.Title)
    dp.register_message_handler(broadcast_title_validation, state=Broadcast.Title)
    dp.register_message_handler(broadcast_description, regexp=re.compile(r'^.{1,800}$'), state=Broadcast.Description)
    dp.register_message_handler(broadcast_description_validation, state=Broadcast.Description)
    dp.register_message_handler(validation_title_description, state=[Broadcast.Title, Broadcast.Description],
                                content_types=['any'])
    dp.register_message_handler(broadcast_photo, state=Broadcast.Photo, content_types=types.ContentType.PHOTO)
    dp.register_message_handler(validation_photo, state=Broadcast.Photo, content_types=['any'])

    dp.register_callback_query_handler(broadcast_send_now, text="broadcast_now",
                                       state=Broadcast.Choose_Sending)

    dp.register_callback_query_handler(broadcast_send_time, text="broadcast_time", state=Broadcast.Choose_Sending)
    dp.register_message_handler(broadcast_text, state=Broadcast.Choose_Sending, content_types=types.ContentType.ANY)

    dp.register_callback_query_handler(broadcast_calendar, calendar_callback.filter(), state=Broadcast.Choose_Calendar)
    dp.register_message_handler(broadcast_calendar_text, state=Broadcast.Choose_Calendar,
                                content_types=types.ContentType.ANY)

    dp.register_message_handler(broadcast_calendar_hour, HourFilter(),
                                state=Broadcast.Choose_Hour)
    dp.register_message_handler(broadcast_calendar_hour_validation, state=Broadcast.Choose_Hour,
                                content_types=types.ContentType.ANY)

    dp.register_message_handler(broadcast_calendar_minute, MinuteFilter(),
                                state=Broadcast.Choose_Minute)
    dp.register_message_handler(broadcast_calendar_minute_validation, state=Broadcast.Choose_Minute,
                                content_types=types.ContentType.ANY)
