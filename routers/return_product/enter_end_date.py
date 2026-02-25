import logging
from datetime import datetime

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.session import async_session_maker, get_user_language
from db.models import Rent
from states import ReturnProduct
from utils.filter_date import is_date
from utils.current_user import get_current_user

router = Router(name=__name__)
logging.basicConfig(level=logging.INFO)


@router.message(F.text.func(is_date), ReturnProduct.entering_end_date)
async def handle_enter_end_date(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    current_user = await get_current_user(message)
    if not current_user:
        await message.answer(
            {"uzl": "Avval /start qiling", "uzk": "Аввал /start қилинг", "rus": "Сначала /start"}[lang]
        )
        await state.clear()
        return

    tenant_id = current_user.tenant_id

    # USER yuborgan sana
    end_date = datetime.strptime(message.text, "%d.%m.%Y").date()  # ✅ DATE

    data = await state.get_data()
    rent_id = data.get("rent_id")

    if not rent_id:
        await message.answer("Ijara topilmadi (state). /return dan qayta boshlang.")
        await state.clear()
        return

    async with async_session_maker() as session:
        rent = await session.scalar(
            select(Rent).where(Rent.id == rent_id, Rent.tenant_id == tenant_id)
        )
        if not rent:
            await message.answer("Ijara topilmadi yoki sizga tegishli emas.")
            await state.clear()
            return

        # ✅ DB ga DATE yozamiz (datetime emas!)
        rent.end_date = end_date
        await session.commit()

    # ✅ state ichida ham saqlab qo'yamiz
    await state.update_data(return_end_date=end_date)

    await message.answer(
        {
            "uzl": f"Tugash sanasi saqlandi: `{end_date}`\nQancha mahsulot qaytarildi?",
            "uzk": f"Тугаш санаси сақланди: `{end_date}`\nҚанча маҳсулот қайтарилди?",
            "rus": f"Дата окончания сохранена: `{end_date}`\nСколько товара вернули?",
        }.get(lang, f"Tugash sanasi saqlandi: `{end_date}`\nQancha mahsulot qaytarildi?"),
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
        }.get(lang, "❌ Sana noto‘g‘ri. Format: `DD.MM.YYYY`"),
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )