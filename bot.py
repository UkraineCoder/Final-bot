import asyncio
import logging
import warnings

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from pytz_deprecation_shim import PytzUsageWarning
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from tgbot.config import load_config, Config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin_panel.add_item import register_add_item
from tgbot.handlers.admin_panel.broadcast import register_broadcast
from tgbot.handlers.admin_panel.change_item import register_change_item
from tgbot.handlers.daily_bonus import register_bonus
from tgbot.handlers.misc_handlers import register_misc
from tgbot.handlers.errors import register_errors
from tgbot.handlers.inline import register_inline
from tgbot.handlers.profile import register_profile
from tgbot.handlers.purchase import register_purchase
from tgbot.handlers.registration import register_registration
from tgbot.handlers.translate import register_language
from tgbot.infrastucture.database.functions.setup import create_session_pool
from tgbot.infrastucture.database.functions.users import get_one_user, add_user
from tgbot.infrastucture.telegraph.service import TelegraphService
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.integration import IntegrationMiddleware
from tgbot.middlewares.language_middlewares import setup_middleware
from tgbot.middlewares.scheduler import SchedulerMiddleware
from tgbot.misc.constants import channels
from tgbot.services.broadcaster import broadcast

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, session_pool, environment: dict, scheduler):
    dp.setup_middleware(DatabaseMiddleware(session_pool))
    dp.setup_middleware(EnvironmentMiddleware(**environment))
    dp.setup_middleware(SchedulerMiddleware(scheduler))
    setup_middleware(dp)


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_language(dp)
    register_broadcast(dp)
    register_bonus(dp)
    register_profile(dp)
    register_purchase(dp)
    register_inline(dp)
    register_change_item(dp)
    register_add_item(dp)
    register_registration(dp)
    register_misc(dp)
    register_errors(dp)


async def on_startup(session_pool, bot: Bot, config: Config):
    logger.info("Bot started")
    await broadcast(bot, config.tg_bot.admin_ids, "Bot started")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2(host='redis_cache',
                            password=config.tg_bot.redis_password) if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    file_uploader = TelegraphService()
    dp = Dispatcher(bot, storage=storage)
    session_pool = await create_session_pool(config.db, echo=False)
    dp.middleware.setup(IntegrationMiddleware(file_uploader))

    job_stores = {
        "default": RedisJobStore(
            host='redis_cache', password=config.tg_bot.redis_password,
            jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running"
        )
    }

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))

    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(config, declared_class=Config)
    scheduler.ctx.add_instance(session_pool, declared_class=sessionmaker)

    warnings.filterwarnings(action="ignore", category=PytzUsageWarning)

    bot['config'] = config

    register_all_middlewares(
        dp,
        session_pool=session_pool,
        environment=dict(config=config),
        scheduler=scheduler
    )
    register_all_filters(dp)
    register_all_handlers(dp)

    await on_startup(session_pool, bot, config)
    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
