import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import CallbackQuery

from tgbot.handlers.misc_handlers import main_menu
from tgbot.infrastucture.database.functions.item_func import get_one_item, update_item
from tgbot.infrastucture.database.functions.users import get_balance, update_user
from tgbot.infrastucture.database.models.item import Item
from tgbot.infrastucture.database.models.users import User
from tgbot.keyboards.inline.buy_button import buy_item, buy_product, payment_menu, \
    buy_card, buy_balance, buy_cancel
from tgbot.keyboards.inline.main_buttons import main_back_button
from tgbot.misc.delete_markup import delete_markup
from tgbot.misc.item_compilation import product
from tgbot.misc.states import Quantity, BuyItem
from tgbot.misc.i18n import _


async def show_item(message: types.Message, session):
    deep_link_args = message.get_args()[3:]

    item = await get_one_item(session, id=int(deep_link_args))

    if item:
        text = _("📫 Артикл: {id}\n📌 Название: {title}\n💎 Количество: {quantity}\n "
                 "📝 Описание: {description}\n💰 Цена: {price}"). \
            format(id=item.id, title=item.title, quantity=item.quantity, description=item.description, price=item.price)

        await message.answer_photo(
            photo=item.photo_link,
            caption=text, reply_markup=buy_item(item.id, item.quantity))
    else:
        await message.answer(_("❌ Товар был удален!"))


async def item_quantity(call: CallbackQuery, callback_data: dict, state: FSMContext, session):
    await call.answer()
    await call.message.delete()

    item = await get_one_item(session, id=int(callback_data.get("id")))

    if item:
        msg = await call.message.answer(_("✏️ Укажите количество товара"), reply_markup=buy_cancel())

        await state.update_data(id=callback_data.get("id"), quantity=callback_data.get("quantity"), msg=msg.message_id)

        await Quantity.Quantity.set()
    else:
        await call.message.answer(_("❌ Товар был удален!"))


async def item_payment_error(message: types.Message, state: FSMContext):
    await delete_markup(message, state)
    msg = await message.answer(_("❌ Ошибка!\n🔖 Укажите верное количество товара"), reply_markup=buy_cancel())
    await state.update_data(msg=msg.message_id)


async def item_payment(message: types.Message, session, state: FSMContext):
    data = await state.get_data()

    id = data['id']
    quantity = int(data['quantity'])
    current_quantity = message.text
    current_quantity_int = int(message.text)

    balance = await get_balance(session, message.from_user.id)

    item = await get_one_item(session, id=int(id))

    if item:
        await delete_markup(message, state)
        if current_quantity_int == 0:
            msg = await message.answer(_("❌ Ошибка!\n Количество товаров не должно быть ноль"),
                                       reply_markup=buy_cancel())
            await state.update_data(msg=msg.message_id)
        elif quantity >= current_quantity_int:
            await message.answer(_("✅ Отлично!\nОсталось оплатить товар!\n\n"
                                   "💰 Ваш баланс: {balance} ₴").format(balance=balance),
                                 reply_markup=payment_menu(id, current_quantity, int(message.message_id) + 1))

            await state.finish()
        else:
            msg = await message.answer(_("❌ Ошибка!\n🔖 Не хватает товара на складе\nВ наличии {quantity}")
                                       .format(quantity=quantity),
                                       reply_markup=buy_cancel())
            await state.update_data(msg=msg.message_id)
    else:
        await message.answer(_("❌ Товар был удален!"))
        await state.finish()


async def item_balance(call: CallbackQuery, callback_data: dict, session):
    id = int(callback_data.get("id"))
    quantity = int(callback_data.get("quantity"))

    item = await get_one_item(session, id=id)

    balance = await get_balance(session, call.from_user.id)

    if item:
        if balance == 0 or balance < item.price * quantity:
            await call.answer(_("У вас недостаточно средств"), show_alert=True)
        elif item.quantity >= quantity:
            await call.message.delete()

            current_quantity = item.quantity - quantity

            total_balance = int(balance) - (item.price * quantity)

            await call.message.answer(text=_("Спасибо за покупку! Ожидайте отправку"),
                                      reply_markup=main_back_button())

            await update_item(session, Item.id == id, quantity=current_quantity)
            await update_user(session, User.telegram_id == call.from_user.id, balance=total_balance)
        else:
            await call.message.delete()
            await call.message.answer(text=_("❌ Ошибка.\n"
                                             "На складе уже не хватает столько товаров.\n"
                                             "Попробуйте заказать еще раз! /start"))
    else:
        await call.message.delete()
        await call.message.answer(_("❌ Товар был удален!"))


async def item_card(call: CallbackQuery, callback_data: dict, session, state: FSMContext):
    await call.answer()

    id = callback_data.get("id")
    quantity = int(callback_data.get("quantity"))
    msg = callback_data.get("msg")

    item = await get_one_item(session, id=int(id))

    if item:
        Product = product(item, quantity)

        msg_one = await call.message.bot.send_invoice(chat_id=call.from_user.id,
                                                      **Product.generate_invoice(),
                                                      payload=id)

        await BuyItem.Address.set()

        await state.update_data(id=item.id, quantity=quantity, msg=msg, msg_one=msg_one.message_id)
    else:
        await call.message.delete()
        await call.message.answer(_("❌ Товар был удален!"))
        await state.finish()


async def choose_shipping(query: types.ShippingQuery):
    POST_REGULAR_SHIPPING = types.ShippingOption(
        id='post_reg',
        title=_('Почтой'),
        prices=[
            types.LabeledPrice(
                _('Обычная коробка'), 0),
            types.LabeledPrice(
                _('Почтой обычной'), 1000_00),
        ]
    )

    POST_FAST_SHIPPING = types.ShippingOption(
        id='post_fast',
        title=_('Почтой (vip)'),
        prices=[
            types.LabeledPrice(
                _('Супер прочная коробка'), 1000_00),
            types.LabeledPrice(
                _('Почтой срочной - DHL (3 дня)'), 3000_00),
        ]
    )

    await query.bot.answer_shipping_query(shipping_query_id=query.id,
                                          shipping_options=[POST_FAST_SHIPPING, POST_REGULAR_SHIPPING],
                                          ok=True)
    await BuyItem.Pay.set()


async def payment_text(message: types.Message):
    await message.answer(_("❗️ Выберите кнопку"))


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, session, state: FSMContext):
    data = await state.get_data()

    id = int(data['id'])
    quantity = data['quantity']
    msg = int(data['msg'])
    msg_one = int(data['msg_one'])

    item = await get_one_item(session, id=id)

    await pre_checkout_query.bot.delete_message(chat_id=pre_checkout_query.from_user.id, message_id=msg)
    await pre_checkout_query.bot.delete_message(chat_id=pre_checkout_query.from_user.id, message_id=msg_one)

    if item:
        if item.quantity >= quantity:
            current_quantity = item.quantity - quantity

            await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
                                                                   ok=True)

            await pre_checkout_query.bot.send_message(chat_id=pre_checkout_query.from_user.id,
                                                      text=_("Спасибо за покупку! Ожидайте отправку"),
                                                      reply_markup=main_back_button())

            await update_item(session, Item.id == id, quantity=current_quantity)
        else:
            await pre_checkout_query.bot.send_message(chat_id=pre_checkout_query.from_user.id,
                                                      text=_("❌ Ошибка.\n"
                                                             "На складе уже не хватает столько товаров.\n"
                                                             "Попробуйте заказать еще раз! /start"))
    else:
        await pre_checkout_query.bot.send_message(chat_id=pre_checkout_query.from_user.id,
                                                  text=_("❌ Товар был удален!"))

    await state.finish()


async def item_cancel(call: CallbackQuery, state: FSMContext):
    await call.answer()

    try:
        data = await state.get_data()

        msg_one = int(data['msg_one'])
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=msg_one)
    except Exception:
        pass

    await main_menu(call)
    await state.finish()


def register_purchase(dp: Dispatcher):
    dp.register_callback_query_handler(item_cancel, text="cancel", state="*")

    dp.register_pre_checkout_query_handler(process_pre_checkout_query, state=BuyItem.Pay)
    dp.register_shipping_query_handler(choose_shipping, state=[BuyItem.Address, '*'])
    dp.register_message_handler(payment_text, state=[BuyItem.Address, BuyItem.Pay], content_types=['any'])

    dp.register_callback_query_handler(item_card, buy_card.filter())
    dp.register_callback_query_handler(item_balance, buy_balance.filter())

    dp.register_message_handler(item_payment, regexp=re.compile(r'^[0-9]+$'), state=Quantity.Quantity)
    dp.register_message_handler(item_payment_error, state=Quantity.Quantity)

    dp.register_callback_query_handler(item_quantity, buy_product.filter())
    dp.register_message_handler(show_item, CommandStart(deep_link=re.compile(r'id_(\d+)')))
