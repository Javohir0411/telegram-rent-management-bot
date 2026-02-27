from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot_strings.enum_str import SIZE_LABEL, TYPE_TO_SIZE
from database.session import get_user_language
from keyboards.common_keyboards import build_select_keyboard, build_yes_or_no_kb
from states import AddProductState
from utils.enums import ProductSizeEnum, ProductTypeEnum

router = Router(name=__name__)


@router.message(AddProductState.are_there_size, F.text.casefold() == "yes")
async def handle_is_there_size_ok(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    await state.update_data(are_there_size=True)

    data = await state.get_data()
    product_type = data.get("inserted_product_type")

    # Agar monolit bo‘lsa, size yo‘q deb "NO" flow ga o‘tkazamiz (xohishingizga qarab)
    if product_type == ProductTypeEnum.monolit or product_type is None:
        await state.update_data(are_there_size=False)
        await state.set_state(AddProductState.insert_product_quantity)

        name = data.get("inserted_product_name", "mahsulot")
        await message.answer(
            text={
                "uzl": f"Mayli, unda nechta *{name}* qo'shmoqchisiz?\nMiqdorni raqam bilan kiriting.",
                "uzk": f"Майли, унда нечта *{name}* қўшмоқчисиз?\nМиқдорни рақам билан киритинг.",
                "rus": f"Хорошо, сколько *{name}* добавить?\nВведите количество цифрами.",
            }.get(lang),
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode="Markdown",
        )
        return

    allowed_sizes = TYPE_TO_SIZE.get(product_type, [])
    kb_label = [SIZE_LABEL[lang][s] for s in allowed_sizes]  # ✅ faqat keraklilar

    await state.set_state(AddProductState.insert_product_size)

    await message.answer(
        text={
            "uzl": f"*{data['inserted_product_name']}* uchun hajmni tanlang",
            "uzk": f"*{data['inserted_product_name']}* учун ҳажмни танланг",
            "rus": f"Выберите размер для *{data['inserted_product_name']}*",
        }.get(lang),
        reply_markup=build_select_keyboard(kb_label),
        parse_mode="Markdown",
    )


@router.message(AddProductState.are_there_size, F.text.casefold() == "no")
async def handle_is_there_size_no(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    await state.update_data(are_there_size=False)
    data = await state.get_data()
    name = data.get("inserted_product_name")
    await state.set_state(AddProductState.insert_product_quantity)
    await message.answer(
        text={
            "uzl": f"Mayli, unda nechta *{name}* qo'shmoqchi ekanligizni faqat raqam ko'rinishida yozing",
            "uzk": f"Майли, унда нечта *{name}* қўшмоқчи эканлигизни фақат рақам кўринишида ёзинг",
            "rus": f"Хорошо, тогда просто напишите, сколько *{name}* вы хотите добавить в виде чисел.",
        }.get(lang, f"Майли, унда нечта *{name}* қўшмоқчи эканлигизни фақат рақам кўринишида ёзинг"),
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )


@router.message(AddProductState.are_there_size)
async def handle_is_there_size_invalid(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    await message.answer(
        text={
            "uzl": "Iltimos, faqat quyidagi tugmalar orqali javob bering. 👇",
            "uzk": "Илтимос, фақат қуйидаги тугмалар орқали жавоб беринг. 👇",
            "rus": "Пожалуйста, отвечайте только с помощью кнопок ниже. 👇",
        }.get(lang, "Илтимос, фақат қуйидаги тугмалар орқали жавоб беринг. 👇"),
        reply_markup=build_yes_or_no_kb(),
    )
