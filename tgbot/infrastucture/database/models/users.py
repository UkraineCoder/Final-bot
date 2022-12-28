from typing import List

from sqlalchemy import Column, VARCHAR, BIGINT, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from tgbot.infrastucture.database.models.base import Base, TimeStampMixin


class User(Base, TimeStampMixin):
    __tablename__ = 'users'

    telegram_id = Column(BIGINT, nullable=False, autoincrement=False, primary_key=True)
    first_name = Column(VARCHAR(200), nullable=False)
    last_name = Column(VARCHAR(200), server_default=expression.null(), nullable=True)
    username = Column(VARCHAR(200), server_default=expression.null(), nullable=True)
    role = Column(VARCHAR(20), nullable=False)
    language = Column(VARCHAR(50), nullable=True)
    bonus_time = Column(TIMESTAMP(timezone=False), nullable=True)
    balance = Column(Integer, nullable=True)

    referrer_id = Column(
        BIGINT,
        ForeignKey("users.telegram_id", ondelete="SET NULL", name="FK__users_referrer_id"),
        nullable=True
    )

    referrer: "User" = relationship(
        "User",
        back_populates="referrals",
        lazy="joined",
        remote_side=[telegram_id],
        join_depth=1
    )

    referrals: List["User"] = relationship(
        "User",
        remote_side=[referrer_id],
        back_populates="referrer",
        lazy="joined",
        join_depth=1,
        order_by='User.created_at.desc()'
    )

