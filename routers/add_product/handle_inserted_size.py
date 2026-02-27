from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot_strings.enum_str import SIZE_LABEL, TYPE_TO_SIZE
from database.session import get_user_language
from keyboards.common_keyboards import build_select_keyboard
from states import AddProductState
from utils.enums import ProductSizeEnum

router = Router(name=__name__)


def get_size_from_label(lang: str, text: str):
    for size_enum, label in SIZE_LABEL.get(lang, {}).items():
        if label == text:
            return size_enum
    return None


@router.message(AddProductState.insert_product_size, F.text)
async def handle_inserted_product_size(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    selected_size = get_size_from_label(lang, message.text)
    data = await state.get_data()
    product_type = data.get("inserted_product_type")
    allowed_sizes = TYPE_TO_SIZE.get(product_type, [])
    kb_label = [SIZE_LABEL[lang][s] for s in allowed_sizes]

    if not selected_size:
        await message.answer(
            text={
                "uzl": "Iltimos, tugmalardan birini tanlang.",
                "uzk": "Илтимос, тугмалардан бирини танланг.",
                "rus": "Пожалуйста, выберите одну из кнопок.",
            }.get(lang, "Илтимос, тугмалардан бирини танланг."),
            reply_markup=build_select_keyboard(kb_label)
        )
        return

    # state ga saqlaymiz
    await state.update_data(inserted_product_size=selected_size)

    data = await state.get_data()
    print("SIZE DATA:", data)

    # keyingi state
    await state.set_state(AddProductState.insert_product_quantity)

    product_name = data.get("inserted_product_name", "mahsulot")
    size_label = SIZE_LABEL[lang][selected_size]

    await message.answer(
        text={
            "uzl": f"Ajoyib 👍\n*{product_name} ({size_label})* dan nechta qo‘shmoqchisiz?\n"
                   f"Miqdorni faqat raqam bilan kiriting.",
            "uzk": f"Ажойиб 👍\n*{product_name} ({size_label})* дан нечта қўшмоқчисиз?\n"
                   f"Миқдорни фақат рақам билан киритинг.",
            "rus": f"Отлично 👍\nСколько добавить *{product_name} ({size_label})*?\n"
                   f"Введите количество цифрами.",
        }.get(lang),
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove(),
    )
