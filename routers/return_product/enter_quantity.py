import logging
from datetime import date

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.session import get_user_language, async_session_maker
from db.models import Rent
from states import ReturnProduct
from utils.enums import RentStatusEnum, PaymentStatusEnum
from utils.current_user import get_current_user

router = Router(name=__name__)
logging.basicConfig(level=logging.INFO)


@router.message(ReturnProduct.entering_quantity)
async def handle_entering_quantity(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    current_user = await get_current_user(message)
    if not current_user:
        await message.answer(
            {"uzl": "Avval /start qiling", "uzk": "Аввал /start қилинг", "rus": "Сначала /start"}[lang]
        )
        await state.clear()
        return

    tenant_id = current_user.tenant_id

    # 1) User son kiritadi
    try:
        quantity_entered = int(message.text)
        if quantity_entered <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            {
                "uzl": "Qiymatni 0 dan katta son ko'rinishida kiriting!",
                "uzk": "Қийматни 0 дан катта сон кўринишида киритинг!",
                "rus": "Введите число больше 0!",
            }[lang]
        )
        return

    data = await state.get_data()
    rent_id = data.get("rent_id")

    if not rent_id:
        await message.answer("Ijara topilmadi (state). /return dan qayta boshlang.")
        await state.clear()
        return

    async with async_session_maker() as session:
        # 2) Rentni tenant bilan tekshirib olamiz
        result = await session.execute(
            select(Rent)
            .options(selectinload(Rent.product))
            .where(Rent.id == rent_id, Rent.tenant_id == tenant_id)
        )
        rent = result.scalar_one_or_none()

        if not rent:
            await message.answer("Ijara topilmadi yoki sizga tegishli emas.")
            await state.clear()
            return

        returned_qty = rent.returned_quantity or 0
        remaining_now = rent.quantity - returned_qty

        if quantity_entered > remaining_now:
            await message.answer(
                {
                    "uzl": f"Max {remaining_now} dona qaytarish mumkin.",
                    "uzk": f"Максимум {remaining_now} дона қайтариш мумкин.",
                    "rus": f"Можно вернуть максимум {remaining_now}.",
                }[lang]
            )
            return

        # 3) returned_quantity oshiramiz
        rent.returned_quantity = returned_qty + quantity_entered

        # 4) Hammasi qaytdimi? -> returned status
        if rent.returned_quantity >= rent.quantity:
            rent.rent_status = RentStatusEnum.returned

            # end_date bo'lmasa bugunni qo'yamiz
            if rent.end_date is None:
                rent.end_date = date.today()

        # 5) Narxni qayta hisoblash (end_date bor bo'lsa)
        if rent.end_date is not None:
            days = (rent.end_date - rent.start_date).days + 1
            if days < 1:
                days = 1

            price_per_day = float(rent.product.price_per_day or 0) if rent.product else 0.0

            # Eslatma:
            # siz hozir product_price ni "asl quantity" bo'yicha hisoblayapsiz (rent.quantity).
            # Agar siz "qaytmagan qismi" bo'yicha hisoblamoqchi bo'lsangiz ayting, o'zgartirib beraman.
            rent.product_price = float(rent.quantity) * price_per_day * float(days)
            rent.rent_price = float(rent.product_price or 0) + float(rent.delivery_price or 0)

        await session.commit()

    await message.answer(
        {
            "uzl": "Mahsulot qaytarildi va ijara yangilandi ✅",
            "uzk": "Маҳсулот қайтарилди ва ижара янгиланди ✅",
            "rus": "Товар возвращён, аренда обновлена ✅",
        }[lang]
    )

    # 6) Endi payment status tanlash tugmalari
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=PaymentStatusEnum.full_paid.value, callback_data="payment_full"),
            InlineKeyboardButton(text=PaymentStatusEnum.part_paid.value, callback_data="payment_part"),
            InlineKeyboardButton(text=PaymentStatusEnum.not_paid.value, callback_data="payment_not"),
        ]]
    )
    await message.answer(
        {
            "uzl": "To‘lov holatini tanlang:",
            "uzk": "Тўлов ҳолатини танланг:",
            "rus": "Выберите статус оплаты:",
        }[lang],
        reply_markup=kb
    )


@router.callback_query(lambda c: c.data and c.data.startswith("payment_"))
async def handle_payment_status(call: types.CallbackQuery, state: FSMContext):
    lang = await get_user_language(call)

    current_user = await get_current_user(call)
    if not current_user:
        await call.answer("Avval /start qiling", show_alert=True)
        await state.clear()
        return

    tenant_id = current_user.tenant_id

    data = await state.get_data()
    rent_id = data.get("rent_id")

    if not rent_id:
        await call.answer("Ijara topilmadi (state)", show_alert=True)
        return

    payment_mapping = {
        "payment_full": PaymentStatusEnum.full_paid,
        "payment_part": PaymentStatusEnum.part_paid,
        "payment_not": PaymentStatusEnum.not_paid,
    }
    payment_status = payment_mapping.get(call.data)
    if not payment_status:
        await call.answer("Xatolik!", show_alert=True)
        return

    async with async_session_maker() as session:
        rent = await session.scalar(
            select(Rent).where(Rent.id == rent_id, Rent.tenant_id == tenant_id)
        )
        if not rent:
            await call.message.answer("Ijara topilmadi yoki sizga tegishli emas.")
            await state.clear()
            return

        rent.status = payment_status
        await session.commit()

    await call.message.edit_text(
        {
            "uzl": f"To‘lov holati yangilandi: {payment_status.value}",
            "uzk": f"Тўлов ҳолати янгиланди: {payment_status.value}",
            "rus": f"Статус оплаты обновлён: {payment_status.value}",
        }.get(lang, f"To‘lov holati yangilandi: {payment_status.value}")
    )

    await call.answer("✅")
    await state.clear()