from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.session import async_session_maker
from db.models import Renter, Rent, Product
from utils.enums import RentStatusEnum, PaymentStatusEnum


async def save_rent_from_fsm(fsm_data: dict):
    tenant_id = fsm_data.get("tenant_id")
    if tenant_id is None:
        raise ValueError("FSM data ichida tenant_id yo'q. state.update_data(tenant_id=...) qiling.")

    async with async_session_maker() as session:  # type: AsyncSession

        # 1) Renter saqlash (✅ tenant_id shart)
        renter = Renter(
            tenant_id=tenant_id,
            renter_fullname=fsm_data["renter_fullname"],
            renter_phone_number=fsm_data["renter_phone_number"],
            renter_passport_info=fsm_data.get("passport_info"),
        )
        session.add(renter)
        await session.flush()

        start_date = fsm_data["start_date"]
        end_date = fsm_data.get("end_date")

        days = None
        if end_date is not None:
            days = (end_date - start_date).days + 1
            if days < 1:
                days = 1

        delivery_price = (
            fsm_data.get("price_delivery", 0)
            if fsm_data.get("distance_km", 0) > 0
            else 0
        )

        # 2) Rentlarni saqlash (✅ tenant_id shart)
        for item in fsm_data["rent_info"]:
            query = (
                select(Product)
                .where(Product.tenant_id == tenant_id)  # ✅ product ham shu tenantniki
                .where(Product.product_type == item["product_type"])
                .where(
                    Product.product_size.is_(None)
                    if item.get("product_size") is None
                    else Product.product_size == item["product_size"]
                )
            )
            product = (await session.execute(query)).scalar_one()

            product_price = None
            rent_price = None
            if days is not None:
                product_price = item["quantity"] * (product.price_per_day or 0) * days
                rent_price = product_price + delivery_price

            rent = Rent(
                tenant_id=tenant_id,          # ✅
                user_id=fsm_data["user_id"],  # bu ham kerak
                renter_id=renter.id,
                product_id=product.id,
                quantity=item["quantity"],
                returned_quantity=0,
                start_date=start_date,
                end_date=end_date,
                latitude=fsm_data.get("renter_latitude"),
                longitude=fsm_data.get("renter_longitude"),
                delivery_needed=fsm_data.get("distance_km", 0) > 0,
                delivery_price=delivery_price,
                product_price=product_price,
                rent_price=rent_price,
                comment=fsm_data.get("notes", ""),
                status=PaymentStatusEnum.not_paid,
                rent_status=RentStatusEnum.active,
            )
            session.add(rent)

        await session.commit()

        # 3) Rentlarni qayta yuklash (✅ tenant filter)
        result = await session.execute(
            select(Rent)
            .options(selectinload(Rent.product))
            .where(Rent.tenant_id == tenant_id)      # ✅
            .where(Rent.renter_id == renter.id)
        )
        return result.scalars().all()