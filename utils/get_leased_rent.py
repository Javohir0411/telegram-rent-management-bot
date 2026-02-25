from aiogram import types
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.session import async_session_maker
from db.models import User, Rent
from utils.enums import RentStatusEnum


async def get_leased_rents(event: types.Message | types.CallbackQuery):
    tg_id = event.from_user.id

    async with async_session_maker() as session:
        # 1) current user ni topamiz
        user_result = await session.execute(
            select(User).where(User.telegram_id == tg_id)
        )
        current_user = user_result.scalar_one_or_none()

        if not current_user:
            # ro'yxatdan o'tmagan bo'lsa bo'sh qaytaramiz
            return []

        # 2) tenant bo'yicha filter
        query = (
            select(Rent)
            .where(
                Rent.tenant_id == current_user.tenant_id,
                Rent.rent_status == RentStatusEnum.active,
            )
            .options(
                selectinload(Rent.product),
                selectinload(Rent.renter),
            )
            .order_by(Rent.created_at.desc())
        )

        result = await session.execute(query)
        return result.scalars().all()