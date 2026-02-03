# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload
# from database.session import async_session_maker
# from db.models import Renter, Rent, Product
# from utils.enums import RentStatusEnum, PaymentStatusEnum
# from datetime import datetime
#
#
# async def save_rent_from_fsm(fsm_data: dict):
#     async with async_session_maker() as session:  # type: AsyncSession
#
#         # 1️⃣ Renter saqlash
#         renter = Renter(
#             renter_fullname=fsm_data["renter_fullname"],
#             renter_phone_number=fsm_data["renter_phone_number"],
#             renter_passport_info=fsm_data.get("passport_info"),
#         )
#         session.add(renter)
#         await session.flush()  # renter.id olish uchun
#
#         start_date = fsm_data["start_date"]
#         end_date = fsm_data["end_date"]
#         days = (end_date - start_date).days or 1
#
#         # 2️⃣ Rentlarni saqlash
#         for item in fsm_data["rent_info"]:
#
#             # ⚠️ MUHIM: product_type + product_size bilan aniq topish
#             query = (
#                 select(Product)
#                 .where(Product.product_type == item["product_type"])
#                 .where(Product.product_size.is_(None) if item.get("product_size") is None
#                        else Product.product_size == item["product_size"])
#             )
#             result = await session.execute(query)
#             product = result.scalar_one()  # endi xato bo‘lmaydi
#
#             product_price = item["quantity"] * product.price_per_day * days
#             delivery_price = (
#                 fsm_data.get("price_delivery", 0)
#                 if fsm_data.get("distance_km", 0) > 0
#                 else 0
#             )
#             rent_price = product_price + delivery_price
#
#             rent = Rent(
#                 user_id=fsm_data.get("user_id"),
#                 renter_id=renter.id,
#                 product_id=product.id,
#                 quantity=item["quantity"],
#                 start_date=datetime.combine(start_date, datetime.min.time()),
#                 end_date=datetime.combine(end_date, datetime.min.time()),
#                 latitude=fsm_data.get("renter_latitude"),
#                 longitude=fsm_data.get("renter_longitude"),
#                 delivery_needed=fsm_data.get("distance_km", 0) > 0,
#                 delivery_price=delivery_price,
#                 product_price=product_price,
#                 rent_price=rent_price,
#                 comment=fsm_data.get("notes", ""),
#                 status=PaymentStatusEnum.not_paid,
#                 rent_status=RentStatusEnum.active,
#             )
#
#             session.add(rent)
#
#         # 3️⃣ Commit
#         await session.commit()
#
#         # 4️⃣ Rentlarni product bilan birga QAYTA yuklab olish (MUHIM QISM)
#         result = await session.execute(
#             select(Rent)
#             .options(selectinload(Rent.product))
#             .where(Rent.renter_id == renter.id)
#         )
#
#         rents = result.scalars().all()
#
#         return rents

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.session import async_session_maker
from db.models import Renter, Rent, Product
from utils.enums import RentStatusEnum, PaymentStatusEnum


async def save_rent_from_fsm(fsm_data: dict):
    async with async_session_maker() as session:  # type: AsyncSession

        # 1️⃣ Renter saqlash
        renter = Renter(
            renter_fullname=fsm_data["renter_fullname"],
            renter_phone_number=fsm_data["renter_phone_number"],
            renter_passport_info=fsm_data.get("passport_info"),
        )
        session.add(renter)
        await session.flush()

        start_date = fsm_data["start_date"]
        end_date = fsm_data.get("end_date")  # 🔑 MUHIM

        # days faqat FIXED rejimda bo‘ladi
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

        # 2️⃣ Rentlarni saqlash
        for item in fsm_data["rent_info"]:
            query = (
                select(Product)
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

            # 🔑 Faqat FIXED rejimda hisoblanadi
            if days is not None:
                product_price = item["quantity"] * (product.price_per_day or 0) * days
                rent_price = product_price + delivery_price

            rent = Rent(
                user_id=fsm_data.get("user_id"),
                renter_id=renter.id,
                product_id=product.id,
                quantity=item["quantity"],
                start_date=start_date,  # Date
                end_date=end_date,  # Date yoki None
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

        # 3️⃣ Rentlarni qayta yuklash
        result = await session.execute(
            select(Rent)
            .options(selectinload(Rent.product))
            .where(Rent.renter_id == renter.id)
        )
        return result.scalars().all()
