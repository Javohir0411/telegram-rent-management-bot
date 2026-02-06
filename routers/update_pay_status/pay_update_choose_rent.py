from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot_strings.enum_str import PAYMENT_STATUS
from database.session import get_user_language
from utils.enums import PaymentStatusEnum

router = Router(name=__name__)


@router.callback_query(F.data.startswith("payupd_rent:"))
async def pay_update_choose_rent(call: CallbackQuery, state: FSMContext):
    lang = await get_user_language(call)
    rent_id = int(call.data.split(":")[1])
    await state.update_data(payupd_rent_id=rent_id)

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=PAYMENT_STATUS[lang][PaymentStatusEnum.full_paid.name],
            callback_data=f"payupd_set:{rent_id}:full_paid"),
        InlineKeyboardButton(
            text=PAYMENT_STATUS[lang][PaymentStatusEnum.part_paid.name],
            callback_data=f"payupd_set:{rent_id}:part_paid"),
        InlineKeyboardButton(
            text=PAYMENT_STATUS[lang][PaymentStatusEnum.not_paid.name],
            callback_data=f"payupd_set:{rent_id}:not_paid"),
    ]])

    await call.message.answer(
        {
            "uzl": "Yangi to‘lov holatini tanlang:",
            "uzk": "Янги тўлов ҳолатини танланг:",
            "rus": "Выберите новый статус оплаты:",
        }[lang],
        reply_markup=kb
    )
    await call.answer()
