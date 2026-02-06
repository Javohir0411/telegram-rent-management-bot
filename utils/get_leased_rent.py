from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.session import async_session_maker
from db.models import Rent
from utils.enums import RentStatusEnum


async def get_leased_rents():
    async with async_session_maker() as session:
        query = (
            select(Rent)
            .where(Rent.rent_status == RentStatusEnum.active)
            .options(
                selectinload(Rent.product),
                selectinload(Rent.renter)
            )
            .order_by(Rent.created_at.desc())
        )

        result = await session.execute(query)
        return result.scalars().all()
