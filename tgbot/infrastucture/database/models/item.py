from sqlalchemy import Column, Integer, VARCHAR

from tgbot.infrastucture.database.models.base import Base


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(VARCHAR(50), nullable=True)
    description = Column(VARCHAR(800), nullable=True)
    price = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=True)
    #photo_file_id = Column(VARCHAR(150), nullable=False)
    photo_link = Column(VARCHAR(150), nullable=False)

