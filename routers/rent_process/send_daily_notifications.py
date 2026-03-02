import logging
from datetime import date

from aiogram import Bot
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot_strings.enum_str import PRODUCT_TYPE_LABEL, SIZE_LABEL
from database.config import get_allowed_tg_ids
from database.session import async_session_maker
from db.models import Rent, User
from utils.enums import RentStatusEnum

logging.basicConfig(level=logging.INFO)

labels = {
    "uzl": {
        "product_price": "Mahsulot narxi",
        "delivery": "Yetkazib berish",
        "payment_status": "To'lov holati",
        "total_product": "Umumiy mahsulot narxi",
        "total_delivery": "Umumiy yetkazib berish",
        "total_sum": "Umumiy summa",
        "location": "Manzil",
        "phone_number": "Telefon raqam",
        "passport": "Passport",
        "notes": "Qo‘shimcha"
    },
    "uzk": {
        "product_price": "Маҳсулот нархи",
        "delivery": "Етказиб бериш",
        "payment_status": "Тўлов ҳолати",
        "total_product": "Умумий маҳсулот нархи",
        "total_delivery": "Умумий етказиб бериш",
        "total_sum": "Умумий сумма",
        "location": "Манзил",
        "phone_number": "Телефон рақам",
        "passport": "Паспорт",
        "notes": "Қўшимча"
    },
    "rus": {
        "product_price": "Цена товара",
        "delivery": "Доставка",
        "payment_status": "Статус оплаты",
        "total_product": "Общая цена товаров",
        "total_delivery": "Общая доставка",
        "total_sum": "Общая сумма",
        "location": "Адрес",
        "phone_number": "Номер телефона",
        "passport": "Паспорт",
        "notes": "Дополнительно"
    }
}


async def get_user_language_by_user_id(telegram_id: int, session: AsyncSession) -> str:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    return user.selected_language if user else "rus"


async def send_expired_rent_notification(bot: Bot):
    today = date.today()
    async with async_session_maker() as session:
        result = await session.execute(
            select(Rent)
            .options(
                selectinload(Rent.product),  # product relationship oldindan yuklanadi
                selectinload(Rent.renter),  # renter relationship oldindan yuklanadi
                selectinload(Rent.user),
            )
            .where(
                and_(
                    Rent.end_date <= today,
                    Rent.rent_status == RentStatusEnum.active
                )
            )
        )
        rents = result.scalars().all()
        if not rents:
            logging.info("BUGUN TUGAGAN IJARA TOPILMADI")
            return

        rents_by_tenant: dict[int, list[Rent]] = {}
        for r in rents:
            rents_by_tenant.setdefault(r.tenant_id, []).append(r)
        # Har bir tenant bo'yicha kimga yuborilishini aniqlash
        #   tenant_id = 1 => adminlar
        #   boshqalar => users jadvalidan shu tenant_id dagilar
        admin_ids = list(get_allowed_tg_ids())

        for tenant_id, tenant_rents in rents_by_tenant.items():
            if tenant_id == 1:
                recipient_ids = admin_ids
            else:
                users_res = await session.execute(
                    select(User.telegram_id, User.selected_language)
                    .where(User.tenant_id == tenant_id)
                )
                rows = users_res.all()
                recipient_ids = [tg_id for tg_id, _lang in rows]

            if not recipient_ids:
                continue

            for chat_id in recipient_ids:
                # recipient tilini olish:
                #   - adminlar bo'lsa ham users jadvalidan olinadi
                users_res = await session.execute(
                    select(User.selected_language, User.tenant_id)
                    .where(User.telegram_id == chat_id)
                )
                row = users_res.one_or_none()

                #user bazada bo'lmasa default
                lang = (row[0] if row else "uzk")

                #ADMIN bo'lsa ham tenant_id = 1 ma'lumoti ketishi kerak.
                effective_tenant_id = 1 if tenant_id == 1 else tenant_id

                #shu tenant_rents ichidan faqat effective_tenant_id nikini olamiz
                relevant_rents = [r for r  in tenant_rents if r.tenant_id == effective_tenant_id]
                if not relevant_rents:
                    continue

                # 5) renter bo‘yicha guruhlab text yasaymiz
                renters_dict: dict[int, list[Rent]] = {}
                for rent in relevant_rents:
                    renters_dict.setdefault(rent.renter_id, []).append(rent)

                # har renter uchun alohida blok
                for renter_id, rents_list in renters_dict.items():
                    renter_name = rents_list[0].renter.renter_fullname

                    headers = {
                        "uzl": f"🕖 {renter_name} ijaraga olgan mahsulotlar muddati tugadi:\n\n",
                        "uzk": f"🕖 {renter_name} ижарага олган маҳсулотлар муддати тугади:\n\n",
                        "rus": f"🕖 Срок аренды у клиента {renter_name} истёк:\n\n",
                    }
                    lbl = labels.get(lang, labels["uzk"])
                    text = headers.get(lang, headers["uzk"])

                    total_product_price = 0
                    total_delivery_price = 0

                    for rent in rents_list:
                        line = f"{PRODUCT_TYPE_LABEL[lang][rent.product.product_type]}"
                        if rent.product.product_size:
                            line += f" ({SIZE_LABEL[lang][rent.product.product_size]})"

                        line += f" — {rent.quantity} dona\n"
                        line += f"{lbl['product_price']}: {rent.product_price or 0} so'm\n"
                        line += f"{lbl['delivery']}: {rent.delivery_price or 0} so'm\n"
                        line += f"{lbl['payment_status']}: {rent.status}\n\n"

                        text += line

                        total_product_price += rent.product_price or 0
                        total_delivery_price += rent.delivery_price or 0

                    total_sum = total_product_price + total_delivery_price

                    text += f"\n{lbl['total_product']}: {total_product_price} so'm\n"
                    text += f"{lbl['total_delivery']}: {total_delivery_price} so'm\n"
                    text += f"{lbl['total_sum']}: {total_sum} so'm\n"

                    text += f"📍{lbl['location']}: {rents_list[0].latitude}, {rents_list[0].longitude}\n"
                    text += f"📞 {lbl['phone_number']}: {rents_list[0].renter.renter_phone_number}\n"
                    text += f"🛂 {lbl['passport']}: {rents_list[0].renter.renter_passport_info}\n"
                    text += f"📝 {lbl['notes']}: {rents_list[0].comment or ''}"

                    try:
                        logging.info(f"XABAR YUBORILGAN USERLAR: {chat_id}")
                        await bot.send_message(chat_id=chat_id, text=text)
                    except Exception as e:
                        logging.error(f"XABAR YUBORISHDA XATOLIK chat_id={chat_id}: {e}")
