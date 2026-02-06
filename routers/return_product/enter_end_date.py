import logging
from datetime import datetime

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.session import async_session_maker, get_user_language
from db.models import Rent
from states import ReturnProduct
from utils.filter_date import is_date

router = Router(name=__name__)


@router.message(F.text.func(is_date), ReturnProduct.entering_end_date)
async def handle_enter_end_date(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    end_date = datetime.strptime(message.text, "%d.%m.%Y").date()

    data = await state.get_data()
    rent_id = data.get("rent_id")

    if not rent_id:
        await message.answer(f"{rent_id} topilmadi (state). /return dan qayta boshlang.")
        await state.clear()
        return

    # ✅ DB ga end_date yozib qo‘yamiz
    async with async_session_maker() as session:
        rent = await session.scalar(select(Rent).where(Rent.id == rent_id))
        if not rent:
            await message.answer("Ijara topilmadi")
            await state.clear()
            return

        rent.end_date = datetime.combine(end_date, datetime.min.time())
        await session.commit()

    # ✅ state ichida ham saqlab qo‘yamiz
    await state.update_data(return_end_date=end_date)

    await message.answer(
        {
            "uzl": f"Tugash sanasi saqlandi: `{end_date}`\nQancha mahsulot qaytarildi?",
            "uzk": f"Тугаш санаси сақланди: `{end_date}`\nҚанча маҳсулот қайтарилди?",
            "rus": f"Дата окончания сохранена: `{end_date}`\nСколько товара вернули?",
        }.get(lang, "Тугаш санаси сақланди: *{end_date}*\nҚанча маҳсулот қайтарилди?"),
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )

    await state.set_state(ReturnProduct.entering_quantity)


@router.message(ReturnProduct.entering_end_date)
async def handle_invalid_end_date(message: types.Message):
    lang = await get_user_language(message)
    await message.answer(
        {
            "uzl": "❌ Sana noto‘g‘ri. Format: `DD.MM.YYYY` (masalan: `01.01.2026`)",
            "uzk": "❌ Сана нотўғри. Формат: `DD.MM.YYYY` (масалан: `01.01.2026`)",
            "rus": "❌ Неверная дата. Формат: `DD.MM.YYYY` (например: `01.01.2026`)",
        }.get(lang, "❌ Сана нотўғри. Формат: `DD.MM.YYYY` (масалан: `01.01.2026`)"),
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
