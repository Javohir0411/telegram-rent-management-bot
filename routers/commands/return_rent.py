# return_rent.py
import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.session import async_session_maker, get_user_language
from db.models import Rent, Renter
from keyboards.common_keyboards import build_select_keyboard
from states import ReturnProduct
from utils.enums import RentStatusEnum
from utils.current_user import get_current_user

router = Router(name=__name__)

@router.message(Command("return", prefix="/!"))
async def return_rent(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    await state.clear()

    current_user = await get_current_user(message)
    if not current_user:
        await message.answer({"uzl":"Avval /start qiling","uzk":"Аввал /start қилинг","rus":"Сначала /start"}[lang])
        return

    tenant_id = current_user.tenant_id

    async with async_session_maker() as session:
        # Renterlarni active rent bor bo'lganlari bilan chiqaramiz (tenant bo'yicha)
        result = await session.execute(
            select(Renter)
            .join(Rent, Rent.renter_id == Renter.id)
            .where(
                Rent.tenant_id == tenant_id,
                Renter.tenant_id == tenant_id,
                Rent.rent_status == RentStatusEnum.active,
            )
            .order_by(Renter.id.desc())
        )
        renters = result.scalars().unique().all()

    if not renters:
        await message.answer(
            {
                "uzl": "Hozircha ijaraga berilgan mahsulotlar mavjud emas",
                "uzk": "Ҳозирча ижарага берилган маҳсулотлар мавжуд эмас",
                "rus": "Сейчас активной аренды нет.",
            }[lang]
        )
        return

    kb = build_select_keyboard([f"{r.renter_fullname} (#{r.id})" for r in renters])
    await message.answer(
        {"uzl":"Ijarachini tanlang: ","uzk":"Ижарачини танланг: ","rus":"Выберите арендатора: "}[lang],
        reply_markup=kb
    )
    await state.set_state(ReturnProduct.choosing_renter)