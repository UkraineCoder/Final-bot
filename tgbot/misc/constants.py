from aiogram.utils.helper import Item, Helper, HelperMode
from tgbot.misc.i18n import _


class Roles(Helper):
    mode = HelperMode.lowerCamelCase

    USER = Item()
    ADMIN = Item()
    BOT_OWNER = Item()

    BLOCKED_USER = Item()


# Your channel id
channels = ['']

cancel_text = _("❌ Отменить")
