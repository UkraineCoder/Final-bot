from aiogram.types import LabeledPrice
from tgbot.misc.item import Items


def product(item, quantity):
    Product = Items(
        title=item.title,
        description=item.description,
        currency="UAH",

        prices=[
            LabeledPrice(
                label=f"{item.title} {quantity}",
                amount=(int(item.price) * 100) * quantity
            )
        ],
        max_tip_amount=50_00,
        start_parameter=item.id,
        photo_url=item.photo_link,
        need_shipping_address=True,
        is_flexible=True
    )

    return Product