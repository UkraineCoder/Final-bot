from sqlalchemy import insert, select, or_, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from tgbot.infrastucture.database.models.item import Item


async def add_new_item(session, title, description, price, quantity, photo_link):
    statement = insert(
        Item
    ).values(
        title=title,
        description=description,
        price=price,
        quantity=quantity,
        photo_link=photo_link
    )

    await session.execute(statement)
    await session.commit()


async def get_one_item(session: AsyncSession, **kwargs):
    statement = select(Item).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def item_all(session: AsyncSession):
    statement = select(Item).order_by(Item.title)
    result: AsyncResult = await session.scalars(statement)
    return result.all()


async def item_all_like(session: AsyncSession, word):
    statement = select(Item).filter(or_(Item.title.ilike(f'%{word}%'), Item.description.ilike(f'{word}%'))).order_by(Item.title)

    result: AsyncResult = await session.scalars(statement)
    return result.all()


async def update_item(session: AsyncSession, *clauses, **values):
    statement = update(
        Item
    ).where(
        *clauses
    ).values(
        **values
    )
    await session.execute(statement)
    await session.commit()


async def delete_item(session: AsyncSession, *clauses):
    statement = delete(
        Item
    ).where(
        *clauses
    )
    await session.execute(statement)
    await session.commit()


async def get_count_item(session: AsyncSession, *clauses):
    statement = select(
        func.count(Item.id)
    ).where(
        *clauses
    )
    result: AsyncResult = await session.scalar(statement)
    return result