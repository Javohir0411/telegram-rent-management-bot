import logging

from bot_strings.enum_str import PRODUCT_TYPE_LABEL
from keyboards.common_keyboards import build_select_keyboard
from states import AddProductState
from utils.enums import ProductTypeEnum
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.session import get_user_language

router = Router(name=__name__)


@router.message(Command("add_product", prefix="/!"))
async def add_product(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    logging.info(f"ADD PRODUCT LANGUAGE: {lang}")
    kb_label = [PRODUCT_TYPE_LABEL[lang][t] for t in ProductTypeEnum]
    print(f"TYPE: {kb_label}")
    await state.set_state(AddProductState.insert_product_name)
    await message.answer(
        {
            "uzl": "Ajoyib, quyidagi tugmalarda qo'shmoqchi bo'lgan mahsulotingizni nomini tanlang.",
            "uzk": "Ажойиб, қуйидаги тугмаларда қўшмоқчи бўлган маҳсулотингизни номини танланг.",
            "rus": "Отлично, выберите название товара, который хотите добавить, в кнопках ниже."
        }.get(lang, "Ажойиб, қуйидаги тугмаларда қўшмоқчи бўлган маҳсулотингизни номини танланг."),
        reply_markup=build_select_keyboard(kb_label),
    )
