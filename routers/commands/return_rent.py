import logging

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.session import async_session_maker, get_user_language
from db.models import Rent, Renter
from keyboards.common_keyboards import build_select_keyboard
from states import ReturnProduct
from utils.admin_only import AdminOnly
from utils.enums import RentStatusEnum

router = Router(name=__name__)


@router.message(AdminOnly(), Command("return", prefix="/!"))
async def return_rent(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    async with async_session_maker() as session:
        result = await session.execute(
            select(Renter).join(Rent).where(Rent.rent_status == RentStatusEnum.active)
        )
        renters = result.scalars().unique().all()

        if not renters:
            await message.answer(
                {
                    "uzl": "Hozircha ijaraga berilgan mahsulotlar mavjud emas",
                    "uzk": "Ҳозирча ижарага берилган маҳсулотлар мавжуд эмас",
                    "rus": "В настоящее время товары, доступные для аренды, отсутствуют.",
                }[lang]
            )

        kb = build_select_keyboard([f"{r.renter_fullname} (#{r.id})" for r in renters])
        logging.info(f"KBKBKB: {kb}")
        text = {
            "uzl": "Ijarachini tanlang: ",
            "uzk": "Ижарачини танланг: ",
            "rus": "Выберите арендатора: ",
        }
        await message.answer(text[lang], reply_markup=kb)
        await state.set_state(ReturnProduct.choosing_renter)


@router.message(Command("return", prefix="/!"))
async def return_rent_not_admin(message: types.Message):
    lang = await get_user_language(message)
    await message.answer(
        {
            "uzl": "Sizga ruxsat yo'q ❌\nMa'lumotlar faqat admin uchun",
            "uzk": "Сизга рухсат йўқ ❌\nМаълумотлар фақат админ учун",
            "rus": "Вам запрещено ❌\nИнформация только для администратора.",
        }.get(lang, "Сизга рухсат йўқ ❌\nМаълумотлар фақат админ учун")
    )
