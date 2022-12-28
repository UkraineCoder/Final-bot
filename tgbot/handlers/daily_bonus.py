from datetime import datetime, timedelta
from random import randint
from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from tgbot.infrastucture.database.functions.users import update_user
from tgbot.infrastucture.database.models.users import User
from tgbot.misc.i18n import _


async def bonus(call: CallbackQuery, session, user: User):
    bonus_num = randint(5, 50)

    if datetime.now() < user.bonus_time:
        await call.answer(_("Пока бонус не доступный!\n"
                          "Он станет доступным завтра."),
                          show_alert=True)
    else:
        time = datetime.now() + timedelta(days=1)

        await update_user(session, User.telegram_id == call.from_user.id, balance=user.balance + bonus_num)

        await update_user(session, User.telegram_id == call.from_user.id, bonus_time=time)

        await call.answer(_("Вы получили {bonus_num} ₴!").format(bonus_num=bonus_num), show_alert=True)


def register_bonus(dp: Dispatcher):
    dp.register_callback_query_handler(bonus, text="bonus")
