from sqlalchemy import select, or_, and_

from db.models import User


async def get_user_by_telegram_or_phone(
    db,
    telegram_id: int | None = None,
    phone_number: str | None = None,
    tenant_id: int | None = None,
):
    id_conditions = []

    if telegram_id is not None:
        id_conditions.append(User.telegram_id == telegram_id)

    if phone_number is not None:
        id_conditions.append(User.user_phone_number == phone_number)

    if not id_conditions:
        return None

    base = or_(*id_conditions)

    if tenant_id is not None:
        where_clause = and_(User.tenant_id == tenant_id, base)
    else:
        where_clause = base

    query = select(User).where(where_clause)
    result = await db.execute(query)
    return result.scalar_one_or_none()