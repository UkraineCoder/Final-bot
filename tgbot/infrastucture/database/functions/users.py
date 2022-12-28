from datetime import datetime, timedelta
from typing import Any, Coroutine

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from tgbot.infrastucture.database.models.users import User


async def add_user(session: AsyncSession, telegram_id, first_name, language,
                   last_name=None, username=None, role='user',
                   bonus_time=datetime.now() - timedelta(minutes=1), balance=0):
    insert_stmt = select(
        User
    ).from_statement(
        insert(
            User
        ).values(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            role=role,
            language=language,
            bonus_time=bonus_time,
            balance=balance
        ).returning(User).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_user_id(session: AsyncSession):
    statement = select(User.telegram_id)
    result: AsyncResult = await session.scalars(statement)
    return result.all()


async def get_one_user(session: AsyncSession, **kwargs) -> Coroutine[Any, Any, Any]:
    statement = select(User).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def get_balance(session: AsyncSession, telegram_id):
    statement = select(User.balance).where(User.telegram_id == telegram_id)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def update_user(session: AsyncSession, *clauses, **values):
    statement = update(
        User
    ).where(
        *clauses
    ).values(
        **values
    )
    await session.execute(statement)
    await session.commit()


async def update_users(session: AsyncSession, **values):
    statement = update(
        User
    ).values(
        **values
    )
    await session.execute(statement)
    await session.commit()



