from aiogram.dispatcher.filters.state import StatesGroup, State


class Code(StatesGroup):
    Code = State()


class NewItem(StatesGroup):
    Title = State()
    Description = State()
    Price = State()
    Quantity = State()
    Photo = State()
    Finish = State()


class EditItem(StatesGroup):
    Title = State()
    Description = State()
    Price = State()
    Quantity = State()
    Photo = State()


class Quantity(StatesGroup):
    Quantity = State()


class BuyItem(StatesGroup):
    Address = State()
    Pay = State()


class Broadcast(StatesGroup):
    Title = State()
    Description = State()
    Photo = State()
    Choose_Sending = State()
    Choose_Calendar = State()
    Choose_Hour = State()
    Choose_Minute = State()

