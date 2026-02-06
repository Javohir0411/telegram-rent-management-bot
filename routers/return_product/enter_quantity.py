# import logging
#
# from aiogram import types, Router, F
# from aiogram.fsm.context import FSMContext
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from sqlalchemy import select
#
# from database.session import get_user_language, async_session_maker
# from db.models import Rent
# from states import ReturnProduct
# from utils.enums import RentStatusEnum, PaymentStatusEnum
#
# router = Router(name=__name__)
#
#
# @router.message(ReturnProduct.entering_quantity)
# async def handle_entering_quantity(message: types.Message, state: FSMContext):
#     lang = await get_user_language(message)
#     try:
#         quantity_entered = int(message.text)
#     except ValueError:
#         await message.answer(
#             {
#                 "uzl": "Qiymatni son ko'rinishida kiriting!",
#                 "uzk": "Қийматни сон кўринишида киритинг!",
#                 "rus": "Введите значение в виде числа.!",
#             }[lang]
#         )
#         return
#
#     data = await state.get_data()
#     rent_id = data.get("rent_id")
#
#     async with async_session_maker() as session:
#         result = await session.execute(
#             select(Rent).where(Rent.id == rent_id)
#         )
#         rent = result.scalar_one_or_none()
#         if not rent:
#             await message.answer("Ijara topilmadi")
#             return
#
#         if quantity_entered > rent.quantity:
#             await message.answer(f"Max {rent.quantity} qaytarilishi mumkin")
#             return
#
#         rent.quantity = rent.quantity - quantity_entered
#         if rent.quantity == 0:
#             rent.rent_status = RentStatusEnum.returned
#
#
#         await session.commit()
#         await message.answer(
#             {
#                 "uzl": "Mahsulot qaytarildi va ijara yangilandi ✅",
#                 "uzk": "Маҳсулот қайтарилди ва ижара янгиланди ✅",
#                 "rus": "Товар был возвращен, и договор аренды был продлен. ✅",
#             }[lang]
#         )
#         # 🔹 To'lov holatini so'rash uchun inline keyboard
#         kb = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [
#                     InlineKeyboardButton(text=PaymentStatusEnum.full_paid.value, callback_data="payment_full"),
#                     InlineKeyboardButton(text=PaymentStatusEnum.part_paid.value, callback_data="payment_part"),
#                     InlineKeyboardButton(text=PaymentStatusEnum.not_paid.value, callback_data="payment_not"),
#                 ]
#             ]
#         )
#
#         await message.answer(
#             {
#                 "uzl": "To‘lov holatini tanlang:",
#                 "uzk": "Тўлов ҳолатини танланг:",
#                 "rus": "Выберите статус оплаты:",
#             }[lang],
#             reply_markup=kb
#         )
#
#
# @router.callback_query(F.data.startswith("payment_"))
# async def handle_payment_status(call: types.CallbackQuery, state: FSMContext):
#     lang = await get_user_language(call)
#     logging.info(f"PAYMENT STATUS CALL MESSAGE: {call.message}")
#     data = await state.get_data()
#     rent_id = data.get("rent_id")
#
#     payment_mapping = {
#         "payment_full": PaymentStatusEnum.full_paid,
#         "payment_part": PaymentStatusEnum.part_paid,
#         "payment_not": PaymentStatusEnum.not_paid,
#     }
#
#     payment_status = payment_mapping.get(call.data)
#     if not payment_status:
#         await call.answer("Xatolik!")
#         return
#
#     async with async_session_maker() as session:
#         result = await session.execute(select(Rent).where(Rent.id == rent_id))
#         rent = result.scalar_one_or_none()
#         if not rent:
#             await call.message.answer("Ijara topilmadi")
#             return
#
#         rent.status = payment_status
#         await session.commit()
#
#     await call.message.edit_text(
#         {
#             "uzl": f"To‘lov holati yangilandi: {payment_status.value}",
#             "uzk": f"Тўлов ҳолати янгиланди: {payment_status.value}",
#             "rus": f"Статус оплаты обновлён: {payment_status.value}",
#         }.get(lang, "Тўлов ҳолати янгиланди: {payment_status.value}")
#     )
#
#     await state.clear()


import logging
from datetime import date

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.orm import selectinload

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

    async with async_session_maker() as session:
        result = await session.execute(
            select(Rent)
            .options(selectinload(Rent.product))  # 🔥 product.price_per_day uchun kerak
            .where(Rent.id == rent_id)
        )
        rent = result.scalar_one_or_none()
        if not rent:
            await message.answer("Ijara topilmadi")
            return

        returned_qty = rent.returned_quantity or 0
        remaining_now = rent.quantity - returned_qty  # 🔥 hozir ijarada turgan qismi

        if quantity_entered > remaining_now:
            await message.answer(f"Max {remaining_now} qaytarilishi mumkin")
            return

        # ✅ quantity kamaytirmaymiz, returned_quantity oshiramiz
        rent.returned_quantity = returned_qty + quantity_entered

        # Hammasi qaytdimi?
        if rent.returned_quantity >= rent.quantity:
            rent.rent_status = RentStatusEnum.returned

            # end_date yo‘q bo‘lsa, bugunni qo‘yib yuborish (xohlasangiz)
            if rent.end_date is None:
                rent.end_date = date.today()

        # 🔥 end_date bo‘lsa narxni qayta hisoblaymiz (asl quantity bo‘yicha)
        if rent.end_date is not None:
            days = (rent.end_date - rent.start_date).days + 1
            if days < 1:
                days = 1

            price_per_day = (rent.product.price_per_day or 0) if rent.product else 0
            rent.product_price = rent.quantity * price_per_day * days
            rent.rent_price = (rent.product_price or 0) + (rent.delivery_price or 0)

        await session.commit()

    await message.answer(
        {
            "uzl": "Mahsulot qaytarildi va ijara yangilandi ✅",
            "uzk": "Маҳсулот қайтарилди ва ижара янгиланди ✅",
            "rus": "Товар возвращён, аренда обновлена ✅",
        }[lang]
    )

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
