# choose_product.py
import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot_strings.enum_str import PRODUCT_TYPE_LABEL
from database.session import get_user_language, async_session_maker
from db.models import Rent
from states import ReturnProduct
from utils.enums import RentStatusEnum
from utils.current_user import get_current_user

router = Router(name=__name__)

@router.message(ReturnProduct.choosing_product)
async def product_selected(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    product_text = message.text
    product_text_wo_q = product_text.split("(")[0].strip()

    data = await state.get_data()
    renter_id = data.get("renter_id")

    current_user = await get_current_user(message)
    if not current_user:
        await message.answer({"uzl":"Avval /start qiling","uzk":"Аввал /start қилинг","rus":"Сначала /start"}[lang])
        return

    tenant_id = current_user.tenant_id

    async with async_session_maker() as session:
        result = await session.execute(
            select(Rent)
            .options(selectinload(Rent.product))
            .where(
                Rent.tenant_id == tenant_id,
                Rent.renter_id == renter_id,
                Rent.rent_status == RentStatusEnum.active,
            )
        )
        active_rents = result.scalars().all()

        rent = None
        for r in active_rents:
            label = PRODUCT_TYPE_LABEL[lang][r.product.product_type.value]
            if label == product_text_wo_q:
                rent = r
                break

        if not rent:
            await message.answer("Mahsulot topilmadi, qayta urinib ko‘ring.")
            return

        await state.update_data(rent_id=rent.id)

        if rent.end_date is None:
            await message.answer(
                {
                    "uzl": "Tugash sanasini kiriting (`DD.MM.YYYY`)\nMasalan: `01.01.2026`",
                    "uzk": "Тугаш санасини киритинг (`DD.MM.YYYY`)\nМасалан: `01.01.2026`",
                    "rus": "Введите дату окончания (`DD.MM.YYYY`)\nНапример: `01.01.2026`",
                }[lang],
                reply_markup=types.ReplyKeyboardRemove(),
                parse_mode="Markdown",
            )
            await state.set_state(ReturnProduct.entering_end_date)
        else:
            await state.update_data(return_end_date=rent.end_date)
            await message.answer(
                {
                    "uzl": f"Tugash sanasi mavjud: {rent.end_date}\nQancha mahsulot qaytarildi?",
                    "uzk": f"Тугаш санаси мавжуд: {rent.end_date}\nҚанча маҳсулот қайтарилди?",
                    "rus": f"Дата окончания уже задана: {rent.end_date}\nСколько товара вернули?",
                }[lang],
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.set_state(ReturnProduct.entering_quantity)