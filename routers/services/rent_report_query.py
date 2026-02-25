from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_
from db.models import Rent
from datetime import date


async def get_rents_for_report(
    session,
    tenant_id: int,
    user_db_id: int,
    start_date: date,
    end_date: date
):
    stmt = (
        select(Rent)
        .options(
            selectinload(Rent.renter),
            selectinload(Rent.product),
        )
        .where(
            and_(
                Rent.tenant_id == tenant_id,   # ✅ tenant filter
                Rent.user_id == user_db_id,    # ✅ shu user (admin)
                Rent.start_date <= end_date,
                or_(
                    Rent.end_date.is_(None),
                    Rent.end_date >= start_date,
                ),
            )
        )
        .order_by(Rent.start_date.asc(), Rent.id.asc())
    )

    result = await session.execute(stmt)
    return result.scalars().all()