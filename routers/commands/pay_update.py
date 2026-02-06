from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from database.session import get_user_language, async_session_maker
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router, types
from db.models import Renter
import logging

from states import PayUpdateState
from utils.admin_only import AdminOnly

logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
router = Router(name=__name__)


@router.message(AdminOnly(), Command("pay_update", prefix="/!"))
async def handle_pay_update_command(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    await state.clear()

    async with async_session_maker() as session:
        renters = (
            await session.execute(
                select(Renter)
                .order_by(Renter.id.desc()).limit(20)
            )
        ).scalars().all()

    if not renters:
        logging.warning(f"RENTERS TOPILMADI !!!")
        await message.answer(
            text={
                "uzl": "Ijarachi topilmadi.",
                "uzk": "Ижарачи топилмади.",
                "rus": "Арендатор не найден."
            }.get(lang, "Ижарачи топилмади."),
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return
    for renter in renters:
        logging.info(f"RENTER TOPILDI: {renter.renter_fullname, renter.renter_phone_number} ")
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{r.renter_fullname} ({r.renter_phone_number})",
                callback_data=f"payupd_renter:{r.id}"
            )]
            for r in renters
        ]
    )
    await state.set_state(PayUpdateState.choosing_renter)
    await message.answer(
        {
            "uzl": "Qaysi ijarachining to‘lovini yangilaymiz? (oxirgi 20 ta)",
            "uzk": "Қайси ижарачининг тўловини янгилаймиз? (охирги 20 та)",
            "rus": "Чей платёж обновляем? (последние 20)",
        }.get(lang, "Қайси ижарачининг тўловини янгилаймиз? (охирги 20 та)"),
        reply_markup=kb
    )


@router.message(Command("pay_update", prefix="/!"))
async def handle_pay_update_command_not_admin(message: types.Message):
    lang = await get_user_language(message)
    await message.answer(
        {
            "uzl": "Sizga ruxsat yo'q ❌\nMa'lumotlar faqat admin uchun",
            "uzk": "Сизга рухсат йўқ ❌\nМаълумотлар фақат админ учун",
            "rus": "Вам запрещено ❌\nИнформация только для администратора.",
        }.get(lang, "Сизга рухсат йўқ ❌\nМаълумотлар фақат админ учун")
    )
