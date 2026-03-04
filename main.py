from datetime import datetime, time, timedelta

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import create_async_engine

from routers import router as main_router
import asyncio
import logging
from database.base import Base
from database.config import settings
from routers.rent_process.send_daily_notifications import send_expired_rent_notification

logging.basicConfig(level=logging.INFO)


async def init_db():
    # Jadvalarni yaratish (agar mavjud bo‘lmasa)
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def schedule_daily(bot: Bot):
    """Tonggi 7 da har kuni send_expired_rent_notifications chaqirish."""
    while True:
        now = datetime.now()
        target = datetime.combine(now.date(), time(2, 0))  # uzb vaqti bo'yicha bugungi 7:00
        if now >= target:
            target += timedelta(days=1)  # agar 7:00dan keyin bo'lsa, ertaga
        sleep_seconds = (target - now).total_seconds()
        logging.info(f"Next daily rent check in {sleep_seconds / 3600:.2f} hours")
        await asyncio.sleep(sleep_seconds)
        try:
            await send_expired_rent_notification(bot)
        except Exception as e:
            logging.error(f"Error in daily rent notifications: {e}")


async def main():

    await init_db()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(main_router)

    # Schedulerni ishga tushirish
    asyncio.create_task(schedule_daily(bot))

    # Bot polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
