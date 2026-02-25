from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User


async def get_user_by_telegram_or_phone(
    db: AsyncSession,
    telegram_id: int | None = None,
    phone_number: str | None = None,
    tenant_id: int | None = None,
):
    conditions = []

    if telegram_id is not None:
        conditions.append(User.telegram_id == telegram_id)

    if phone_number is not None:
        conditions.append(User.user_phone_number == phone_number)

    if tenant_id is not None:
        conditions.append(User.tenant_id == tenant_id)

    if not conditions:
        return None

    query = select(User).where(or_(*conditions))

    result = await db.execute(query)
    return result.scalar_one_or_none()