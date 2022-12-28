import re
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.markdown import hlink
from tgbot.infrastucture.database.functions.users import update_user, get_one_user, get_balance
from tgbot.infrastucture.database.models.users import User
from tgbot.keyboards.inline.main_buttons import main_user_button, main_admin_button, admin_keyboard
from tgbot.keyboards.inline.registration_buttons import check_button, registration, invitation_button
from tgbot.misc import subscription
from tgbot.misc.constants import channels
from tgbot.misc.delete_markup import delete_markup
from tgbot.misc.states import Code
from tgbot.misc.i18n import _


def get_mention(user: User):
    first_name = user.first_name
    last_name = user.last_name or ''
    return hlink(f'{first_name} {last_name}', f'tg://user?id={user.telegram_id}')


def registered(check_user, referral_link):
    return (_("Поздравляю, вы получили доступ! 🎉\n"
              "Вы были приглашены пользователем {check_user}!\n"
              "Вы можете получить 10 бонусных гривен, если пригласите рефералов\n"
              "Ваша реферальная ссылка: {referral_link}")
            .format(check_user=get_mention(check_user), referral_link=referral_link))


async def user_start(message: Message, user: User):
    if user.referrer:
        await message.answer(_("🗂 Главное меню"), reply_markup=main_user_button())
    else:
        await message.answer(_("❌ Ошибка \n"
                               "У Вас нет доступа! \n"
                               "Чтобы использовать этого бота введите код приглашения, \n"
                               "либо пройдите по реферальной ссылке"), reply_markup=registration())


async def admin_start(message: Message):
    await message.answer(_("🗂 Главное меню"), reply_markup=main_admin_button())


async def admin_back_menu(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(_("🗂 Главное меню"), reply_markup=main_admin_button())


async def admin_panel(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(_("🎛 Административная панель"), reply_markup=admin_keyboard())


async def invitation_code(call: CallbackQuery, user: User, state: FSMContext):
    await call.answer()

    if not user.referrer:
        await call.message.edit_text(_("✏️ Введите код приглашения:"), reply_markup=invitation_button())
        await Code.Code.set()
        await state.update_data(msg=call.message.message_id)
    else:
        await call.message.answer(_("Вас уже пригласил {referrer}!").format(referrer=get_mention(user.referrer)))


async def invitation_check(message: Message, state: FSMContext, session, user: User):
    referrer_id = int(message.text)

    referrer = await get_one_user(session, telegram_id=referrer_id)

    if referrer:
        await delete_markup(message, state)

        if referrer_id == user.telegram_id:
            await message.answer(_("Вы не можете пригласить сами себя!"))
            return

        balance = await get_balance(session, referrer_id)

        await update_user(session, User.telegram_id == referrer_id, balance=balance + 10)

        await update_user(session, User.telegram_id == user.telegram_id, referrer_id=referrer_id)

        referral_link = await get_start_link(f'referral-{message.from_user.id}', encode=True)

        await message.answer(registered(referrer, referral_link), reply_markup=main_user_button())
        await message.bot.send_message(referrer.telegram_id, _("У вас новый реферал: {user}!")
                                       .format(user=get_mention(user)))

        await state.finish()
    else:
        await delete_markup(message, state)
        msg = await message.answer(_("❌ Ошибка \n"
                                     "Код неверный"), reply_markup=invitation_button())
        await state.update_data(msg=msg.message_id)


async def invitation_check_error(message: Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка \n"
                                 "Код может состоять только из цифр!"), reply_markup=invitation_button())
    await state.update_data(msg=msg.message_id)


async def invitation_back(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await delete_markup(call.message, state)

    await call.message.edit_text(_("❌ Ошибка \n"
                                   "У Вас нет доступа! \n"
                                   "Чтобы использовать этого бота введите код приглашения, \n"
                                   "либо пройдите по реферальной ссылке"), reply_markup=registration())

    await state.finish()


async def subscribe_check(call: CallbackQuery):
    await call.answer()

    channels_format = str()
    for channel in channels:
        chat = await call.bot.get_chat(channel)
        invite_link = await chat.export_invite_link()
        channels_format += f"Канал <a href='{invite_link}'>{chat.title}</a>\n\n"

    await call.message.edit_text(_("Вам необходимо подписаться на следующий канал: \n"
                                 "{channels_format}").format(channels_format=channels_format),
                                 reply_markup=check_button(),
                                 disable_web_page_preview=True)


async def checker_subs(call: CallbackQuery, session, user: User):
    await call.answer()

    if not user.referrer:
        result = str()
        for channel in channels:
            status = await subscription.check(user_id=call.from_user.id,
                                              channel=channel)
            channel = await call.bot.get_chat(channel)
            if status:
                check_user = await get_one_user(session, telegram_id=channel)

                result += _("Подписка на канал <b>{channel_title}</b> Оформлена!\n\n")\
                    .format(channel_title=channel.title)
                await update_user(session, User.telegram_id == user.telegram_id, referrer_id=channel)

                referral_link = await get_start_link(f'referral-{call.from_user.id}', encode=True)

                await call.message.edit_text(result, disable_web_page_preview=True)
                await call.message.answer(registered(check_user, referral_link), reply_markup=main_user_button())
            else:
                invite_link = await channel.export_invite_link()
                result = _("Подписка на канал <b>{channel_title}</b> не оформлена! "
                           "<a href='{invite_link}'>Нужно подписаться.</a>\n\n")\
                    .format(channel_title=channel.title, invite_link=invite_link)
                await call.message.answer(result, disable_web_page_preview=True)
    else:
        await call.message.answer(_("Вас уже пригласил {referrer}!").format(referrer=get_mention(user.referrer)))


async def start_from_referral_link(message: Message, session, user: User, deep_link: re.match):
    if not user.referrer:
        referrer_id = int(deep_link.group(1))
        referral_link = await get_start_link(f'referral-{message.from_user.id}', encode=True)
        if referrer_id == user.telegram_id:
            await message.answer(_("Вы не можете пригласить сами себя!"))
            return

        balance = await get_balance(session, referrer_id)

        await update_user(session, User.telegram_id == referrer_id, balance=balance + 10)

        await update_user(session, User.telegram_id == user.telegram_id, referrer_id=referrer_id)

        referrer = await get_one_user(session, telegram_id=referrer_id)

        await message.answer(registered(referrer, referral_link), reply_markup=main_user_button())

        await message.bot.send_message(referrer.telegram_id, _("У вас новый реферал: {user}!")
                                       .format(user=get_mention(user)))
    else:
        await message.answer(_("Вас уже пригласил {referrer}!").format(referrer=get_mention(user.referrer)))


def register_registration(dp: Dispatcher):
    dp.register_callback_query_handler(subscribe_check, text="subscribe_channel")
    dp.register_callback_query_handler(checker_subs, text="check_subs")
    dp.register_message_handler(invitation_check, regexp=re.compile(r'^[0-9]+$'), state=Code.Code)
    dp.register_message_handler(invitation_check_error, content_types=['any'], state=Code.Code)
    dp.register_callback_query_handler(invitation_back, text="invitation_back", state=Code.Code)
    dp.register_callback_query_handler(invitation_code, text="invitation_code")

    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(admin_back_menu, text="main_menu")
    dp.register_callback_query_handler(admin_panel, text="admin_panel")

    dp.register_message_handler(start_from_referral_link,
                                CommandStart(deep_link=re.compile(r'referral-(\d+)'), encoded=True))
    dp.register_message_handler(user_start, commands=["start"], state="*")
