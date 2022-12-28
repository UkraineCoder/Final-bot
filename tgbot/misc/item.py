from dataclasses import dataclass
from typing import List
from aiogram.types import LabeledPrice
from tgbot.config import load_config


@dataclass
class Items:
    title: str
    description: str
    start_parameter: str
    currency: str   # валюта
    prices: List[LabeledPrice]
    max_tip_amount: int
    provider_data: dict = None
    photo_url: str = None
    photo_size: int = None
    photo_width: int = None
    photo_height: int = None
    need_name: bool = False
    need_phone_number: bool = False
    need_email: bool = False
    need_shipping_address: bool = False # адрес доставки
    send_phone_number_to_provider: bool = False
    send_email_to_provider: bool = False
    is_flexible: bool = False

    config = load_config(".env")

    provider_token: str = config.tg_bot.liq_pay

    def generate_invoice(self):
        return self.__dict__