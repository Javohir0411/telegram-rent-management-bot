from database.session import get_user_language
from keyboards.common_keyboards import build_select_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from utils.admin_only import AdminOnly
from utils.enums import LanguageEnum
from aiogram import Router, types
from states import Register
import logging


logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)


@router.message( CommandStart())
async def handle_command_start(message: types.Message, state: FSMContext):
    logging.info(f"FOYDALANUVCHI {message.from_user.id} /START COMMANDNI ISHGA TUSHIRDI ")
    await state.set_state(Register.language)
    await message.answer(
        text=f"Салом, {message.from_user.full_name}\nКеракли тилни танланг: ",
        reply_markup=build_select_keyboard(LanguageEnum)
    )
    logging.info(f"state: {Register.language} shu yerda boshlandi")


@router.message(CommandStart())
async def handle_command_start_not_admin(message: types.Message):
    lang = await get_user_language(message)
    await message.answer(
        {
            "uzl": "Sizga ruxsat yo'q❌ \nMa'lumotlar faqat admin uchun",
            "uzk": "Сизга рухсат йўқ ❌ \nМаълумотлар фақат админ учун",
            "rus": "Вам запрещено ❌ \nИнформация только для администратора.",
        }.get(lang, "Сизга рухсат йўқ ❌\nМаълумотлар фақат админ учун")
    )