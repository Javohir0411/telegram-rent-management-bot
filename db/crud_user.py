from sqlalchemy.ext.asyncio import AsyncSession
from .models import User


async def create_user(
        db: AsyncSession,
        telegram_id: int,
        user_fullname: str,
        user_phone_number: str,
        selected_language: str,
        tenant_id: int | None = None, #admin uchun 1 oddiy uchun none
):
    user = User(
        telegram_id=telegram_id,
        user_fullname=user_fullname,
        user_phone_number=user_phone_number,
        selected_language=selected_language,
        tenant_id = tenant_id if tenant_id is not None else 0, #muhim:NULL emas
    )
    db.add(user)
    await db.flush()

    if tenant_id is None:
        user.tenant_id = user.id

    await db.commit()
    await db.refresh(user)
    return user

