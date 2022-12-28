from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import get_start_link

from tgbot.handlers.registration import get_mention
from tgbot.infrastucture.database.models.users import User
from tgbot.keyboards.inline.profile_buttons import profile_ref, profile_ref_back
from tgbot.misc.i18n import _


async def profile_user(call: CallbackQuery, user: User):
    await call.answer()

    referral_link = await get_start_link(f'referral-{call.from_user.id}', encode=True)

    await call.message.edit_text(_("👤 Ваш профиль\n\n"
                                   "🔈  Role: {role}\n"
                                   "💸  Баланс: {balance} ₴\n"
                                   "🔑  Ваш код: {telegram_id}\n"
                                   "🔗  Ваша реферальная ссылка:  {referral_link}")
                                 .format(role=user.role, balance=user.balance, telegram_id=user.telegram_id,
                                         referral_link=referral_link), disable_web_page_preview=True,
                                 reply_markup=profile_ref())


async def show_referrer(call: CallbackQuery, user: User):
    if user.referrer:
        await call.answer()
        await call.message.edit_text(_("Ваш рефер: {referrer}")
                                     .format(referrer=get_mention(user.referrer)), reply_markup=profile_ref_back())
    else:
        await call.answer(_("У вас нет рефера!"), show_alert=True)


async def show_referrals(call: CallbackQuery, user: User):
    if user.referrals:
        await call.answer()

        referrals = '\n'.join(f"{num}. {get_mention(referral)} - {referral.created_at.strftime('%d.%m.%Y %H:%M')}"
                              for num, referral in enumerate(user.referrals, start=1))

        await call.message.edit_text(_("Ваши рефералы: \n{referrals}")
                                     .format(referrals=referrals), reply_markup=profile_ref_back())
    else:
        await call.answer(_("У вас еще нет рефералов!"), show_alert=True)


def register_profile(dp: Dispatcher):
    dp.register_callback_query_handler(show_referrer, text="profile_referrer")
    dp.register_callback_query_handler(show_referrals, text="profile_referrals")
    dp.register_callback_query_handler(profile_user, text="profile", state="*")
