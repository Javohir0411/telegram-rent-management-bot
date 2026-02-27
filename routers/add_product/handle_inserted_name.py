import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot_strings.enum_str import PRODUCT_TYPE_LABEL
from database.session import get_user_language
from keyboards.common_keyboards import build_yes_or_no_kb, build_select_keyboard
from states import AddProductState
from utils.enums import ProductTypeEnum

logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
router = Router(name=__name__)


def get_type_from_label(lang: str, text: str):
    for t, label in PRODUCT_TYPE_LABEL.get(lang, {}).items():
        if label == text:
            return t
    return None


@router.message(F.text, AddProductState.insert_product_name)
async def handle_inserted_product_name(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    inserted_product_name = message.text

    allowed_labels = [PRODUCT_TYPE_LABEL[lang][t] for t in ProductTypeEnum]
    if inserted_product_name in allowed_labels:
        product_type = get_type_from_label(lang, inserted_product_name)

        await state.update_data(
            inserted_product_name=inserted_product_name,
            inserted_product_type=product_type,  # ✅ enum
        )

        await state.set_state(AddProductState.are_there_size)
        await message.answer(
            text={
                "uzl": f"{inserted_product_name}ni hajmi turlichami?\n" "Javobingizni quyidagi tugmalar orqali belgilang",
                "uzk": f"{inserted_product_name}ни ҳажми турличами?\n" "Жавобингизни қуйидаги тугмалар орқали белгиланг",
                "rus": "Размеры добавляемого вами товара могут отличаться?\n" "Пожалуйста, укажите свой ответ, используя кнопки ниже.", }.get(
                lang,
                "Сиз қўшмоқчи бўлган маҳсулотингизни ҳажми турличами?\nЖавобингизни қуйидаги тугмалар орқали белгиланг"),
            reply_markup=build_yes_or_no_kb()
        )
    else:
        print(f"INSERTED INVALID NAME: {inserted_product_name}")
        kb_label = [PRODUCT_TYPE_LABEL[lang][t] for t in ProductTypeEnum]
        await message.reply(
            text={
                "uzl": "Iltimos, quyidagi tugmalardan birini tanlang 👇",
                "uzk": "Илтимос, қуйидаги тугмалардан бирини танланг 👇",
                "rus": "Пожалуйста, выберите одну из кнопок ниже. 👇",
            }.get(lang, "Илтимос, қуйидаги тугмалардан бирини танланг 👇"),
            reply_markup=build_select_keyboard(kb_label)
        )
