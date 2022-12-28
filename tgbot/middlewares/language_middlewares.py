from typing import Tuple, Any

from tgbot.misc.i18n import I18N_DOMAIN, LOCALES_DIR

from aiogram.contrib.middlewares.i18n import I18nMiddleware


class ACLMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):
        *_, data = args
        user = data['user']

        return user.language

    def set_user_locale(self, locale: str):
        self.ctx_locale.set(locale)

    async def trigger(self, action, args):
        if 'update' not in action and 'error' not in action and action.startswith('process'):
            locale = await self.get_user_locale(action, args)
            self.set_user_locale(locale)
            return True


def setup_middleware(dp):
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n