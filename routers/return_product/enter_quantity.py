import logging

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from database.session import get_user_language, async_session_maker
from db.models import Rent
from states import ReturnProduct
from utils.enums import RentStatusEnum, PaymentStatusEnum

router = Router(name=__name__)


@router.message(ReturnProduct.entering_quantity)
async def handle_entering_quantity(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    try:
        quantity_entered = int(message.text)
    except ValueError:
        await message.answer(
            {
                "uzl": "Qiymatni son ko'rinishida kiriting!",
                "uzk": "Қийматни сон кўринишида киритинг!",
                "rus": "Введите значение в виде числа.!",
            }[lang]
        )
        return

    data = await state.get_data()
    rent_id = data.get("rent_id")

    async with async_session_maker() as session:
        result = await session.execute(
            select(Rent).where(Rent.id == rent_id)
        )
        rent = result.scalar_one_or_none()
        if not rent:
            await message.answer("Ijara topilmadi")
            return

        if quantity_entered > rent.quantity:
            await message.answer(f"Max {rent.quantity} qaytarilishi mumkin")
            return

        rent.quantity = rent.quantity - quantity_entered
        if rent.quantity == 0:
            rent.rent_status = RentStatusEnum.returned

        await session.commit()
        await message.answer(
            {
                "uzl": "Mahsulot qaytarildi va ijara yangilandi ✅",
                "uzk": "Маҳсулот қайтарилди ва ижара янгиланди ✅",
                "rus": "Товар был возвращен, и договор аренды был продлен. ✅",
            }[lang]
        )
        # 🔹 To'lov holatini so'rash uchun inline keyboard
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=PaymentStatusEnum.full_paid.value, callback_data="payment_full"),
                    InlineKeyboardButton(text=PaymentStatusEnum.part_paid.value, callback_data="payment_part"),
                    InlineKeyboardButton(text=PaymentStatusEnum.not_paid.value, callback_data="payment_not"),
                ]
            ]
        )

        await message.answer(
            {
                "uzl": "To‘lov holatini tanlang:",
                "uzk": "Тўлов ҳолатини танланг:",
                "rus": "Выберите статус оплаты:",
            }[lang],
            reply_markup=kb
        )


@router.callback_query(F.data.startswith("payment_"))
async def handle_payment_status(call: types.CallbackQuery, state: FSMContext):
    lang = await get_user_language(call)
    logging.info(f"PAYMENT STATUS CALL MESSAGE: {call.message}")
    data = await state.get_data()
    rent_id = data.get("rent_id")

    payment_mapping = {
        "payment_full": PaymentStatusEnum.full_paid,
        "payment_part": PaymentStatusEnum.part_paid,
        "payment_not": PaymentStatusEnum.not_paid,
    }

    payment_status = payment_mapping.get(call.data)
    if not payment_status:
        await call.answer("Xatolik!")
        return

    async with async_session_maker() as session:
        result = await session.execute(select(Rent).where(Rent.id == rent_id))
        rent = result.scalar_one_or_none()
        if not rent:
            await call.message.answer("Ijara topilmadi")
            return

        rent.status = payment_status
        await session.commit()

    await call.message.edit_text(
        {
            "uzl": f"To‘lov holati yangilandi: {payment_status.value}",
            "uzk": f"Тўлов ҳолати янгиланди: {payment_status.value}",
            "rus": f"Статус оплаты обновлён: {payment_status.value}",
        }.get(lang, "Тўлов ҳолати янгиланди: {payment_status.value}")
    )

    await state.clear()
