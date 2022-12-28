from pathlib import Path

from aiogram.contrib.middlewares.i18n import I18nMiddleware

I18N_DOMAIN = 'testbot'

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'

i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)

_ = i18n.gettext
