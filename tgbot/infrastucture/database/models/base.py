from __future__ import annotations
from sqlalchemy import Column, TIMESTAMP, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import declarative_mixin

Base = declarative_base()


@declarative_mixin
class TimeStampMixin:
    __abstract__ = True

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_onupdate=func.now(), server_default=func.now())

