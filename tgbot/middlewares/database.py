import logging
from typing import Dict, Any

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import CallbackQuery, Message, Update
from aiogram.types.base import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.config import load_config
from tgbot.infrastucture.database.functions.users import get_one_user, add_user
from tgbot.misc.constants import Roles, channels


class DatabaseMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["update"]

    def __init__(self, session_pool):
        super().__init__()
        self.__session_pool = session_pool

    async def pre_process(self, obj: [CallbackQuery, Message], data: Dict, *args: Any) -> None:
        session: AsyncSession = self.__session_pool()
        data["session"] = session
        data["session_pool"] = self.__session_pool
        if not getattr(obj, "from_user", None):
            return
        if obj.from_user:
            config = load_config(".env")
            user = await get_one_user(session, telegram_id=obj.from_user.id)

            if not user:
                if obj.from_user.id in config.tg_bot.admin_ids:
                    user = await add_user(
                        session,
                        telegram_id=obj.from_user.id,
                        first_name=obj.from_user.first_name,
                        last_name=obj.from_user.last_name,
                        username=obj.from_user.username,
                        role=Roles.ADMIN,
                        language=obj.from_user.language_code
                    )
                else:
                    user = await add_user(
                        session,
                        telegram_id=obj.from_user.id,
                        first_name=obj.from_user.first_name,
                        last_name=obj.from_user.last_name,
                        username=obj.from_user.username,
                        role=Roles.USER,
                        language=obj.from_user.language_code
                    )
                await session.commit()

            data['user'] = user

    async def post_process(self, obj: TelegramObject, data: Dict, *args: Any) -> None:
        if session := data.get("session", None):
            session: AsyncSession
            await session.close()