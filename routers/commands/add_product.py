import logging

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.session import get_user_language

router = Router(name=__name__)


@router.message(Command("add_product", prefix="/!"))
async def add_product(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    logging.info(f"ADD PRODUCT LANGUAGE: {lang}")
    await message.answer(
        {
            "uzl": "Ajoyib, qo'shmoqchi bo'lgan mahsulotingizni nomini yozing.\n\n"
                   "Faqat bir iltimos, siz qaysi tilni tanlagan bo'lsangiz, mahsulot nomini ham xuddi shu tilda kiriting.",
            "uzk": "Ажойиб, қўшмоқчи бўлган маҳсулотингизни номини ёзинг.\n\n"
                   "Фақат бир илтимос, сиз қайси тилни танлаган бўлсангиз, маҳсулот номини ҳам худди шу тилда киритинг.",
            "rus": "Отлично, введите название товара, который хотите добавить.\n\n"
                   "Одна просьба: независимо от выбранного вами языка, введите название товара на том же языке."
        }.get(lang, "Ажойиб, қўшмоқчи бўлган маҳсулотингизни номини ёзинг.\n\n"
                    "Фақат бир илтимос, сиз қайси тилни танлаган бўлсангиз, маҳсулот номини ҳам худди шу тилда киритинг.")
    )
