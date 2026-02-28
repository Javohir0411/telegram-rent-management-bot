from db.models import User, Tenant

async def create_user(
    db,
    telegram_id: int,
    user_fullname: str,
    user_phone_number: str,
    selected_language: str,
    tenant_id: int | None = None,   # admin uchun 1, oddiy uchun None
):
    #tenant aniqlash
    if tenant_id is None:
        tenant = Tenant(name=f"Tenant for {telegram_id}")
        db.add(tenant)
        await db.flush()  # tenant.id chiqadi
        tenant_id = tenant.id
    else:
        #admin tenant mavjud bo‘lishi kerak (id=1)
        tenant = await db.get(Tenant, tenant_id)
        if tenant is None:
            tenant = Tenant(id=tenant_id, name="Admin tenant")
            db.add(tenant)
            await db.flush()

    #user yaratish
    user = User(
        telegram_id=telegram_id,
        user_fullname=user_fullname,
        user_phone_number=user_phone_number,
        selected_language=selected_language,
        tenant_id=tenant_id,
    )
    db.add(user)

    await db.commit()
    await db.refresh(user)
    return user