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


@router.message(F.text, AddProductState.insert_product_name)
async def handle_inserted_product_name(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    inserted_product_name = message.text
    logging.info(f"INSERTED NAME: {inserted_product_name}")
    allowed_types = [PRODUCT_TYPE_LABEL[lang][t] for t in ProductTypeEnum]
    if inserted_product_name in allowed_types:
        await state.update_data(inserted_product_name=inserted_product_name)
        data = await state.get_data()
        logging.info(f"DATA IN HANDLE INSERTED NAME . PY: {data}")
        await state.set_state(AddProductState.insert_product_size)
        await message.answer(
            text={
                "uzl": f"{inserted_product_name}ni hajmi turlichami?\n"
                       "Javobingizni quyidagi tugmalar orqali belgilang",
                "uzk": f"{inserted_product_name}ни ҳажми турличами?\n"
                       "Жавобингизни қуйидаги тугмалар орқали белгиланг",
                "rus": "Размеры добавляемого вами товара могут отличаться?\n"
                       "Пожалуйста, укажите свой ответ, используя кнопки ниже.",

            }.get(
                lang,
                "Сиз қўшмоқчи бўлган маҳсулотингизни ҳажми турличами?\nЖавобингизни қуйидаги тугмалар орқали белгиланг"
            ),
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