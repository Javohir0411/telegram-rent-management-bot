import logging

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.session import get_user_language
from keyboards.inlinekeyboard.report_range_kb import report_range_kb
from states import ReportState
from utils.admin_only import AdminOnly

logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)


@router.message(F.text, AdminOnly(), Command("rent_report", prefix="/!"))
async def rent_report_start(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    logging.info(f"RENT REPORT TEXT: {message.text}")
    await message.answer(
        {
            "uzl":"📅 Hisobot oralig‘ini tanlang yoki qo‘lda kiriting:",
            "uzk":"📅 Ҳисобот оралиғини танланг ёки қўлда киритинг:",
            "rus":"📅 Выберите период или введите вручную:",
        }.get(lang, "📅 Ҳисобот оралиғини танланг ёки қўлда киритинг:"),
        reply_markup=report_range_kb(lang)
    )
    await state.set_state(ReportState.get_start_end_dates)


@router.message(F.text, Command("rent_report", prefix="/!"))
async def rent_report_no_access(message: types.Message):
    lang = await get_user_language(message)
    await message.answer(
        {
            "uzl": "Sizga ruxsat yo'q ❌\nMa'lumotlar faqat admin uchun",
            "uzk": "Сизга рухсат йўқ ❌\nМаълумотлар фақат админ учун",
            "rus": "Вам запрещено ❌\nИнформация только для администратора.",
        }.get(lang, "Сизга рухсат йўқ ❌\nМаълумотлар фақат админ учун")
    )