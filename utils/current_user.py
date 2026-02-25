from aiogram import types
from sqlalchemy import select
from database.session import async_session_maker
from db.models import User

async def get_current_user(event: types.Message | types.CallbackQuery):
    tg_id = event.from_user.id
    async with async_session_maker() as session:
        res = await session.execute(select(User).where(User.telegram_id == tg_id))
        return res.scalar_one_or_none()