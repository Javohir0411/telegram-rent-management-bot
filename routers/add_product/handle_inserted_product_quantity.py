from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from database.session import get_user_language
from states import AddProductState

router = Router(name=__name__)


@router.message(AddProductState.insert_product_quantity, F.text.regexp(r"^\d+$"))
async def handle_inserted_product_quantity_ok(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    quantity = int(message.text)
    await state.update_data(insert_product_quantity=quantity)

    data = await state.get_data()
    print(f"MA'LUMOTLAR: {data}")

    await state.set_state(AddProductState.insert_product_price)

    product_name = data.get("inserted_product_name", "mahsulot")

    await message.answer(
        text={
            "uzl": f"Zo'r, *{product_name}* uchun kunlik narxni necha pul deb belgilaysiz?\n"
                   f"Faqat, narxni raqam ko'rinishida kiriting!",
            "uzk": f"Зўр, *{product_name}* учун кунлик нархни неча пул деб белгилайсиз?\n"
                   f"Фақат, нархни рақам кўринишида киритинг!",
            "rus": f"Отлично, какую дневную цену установить для *{product_name}*?\n"
                   f"Укажите цену только цифрами!",
        }.get(lang),
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )

@router.message(AddProductState.insert_product_quantity)
async def handle_inserted_product_quantity_bad(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    await message.answer(
        text={
            "uzl": "Miqdorni faqat raqam ko'rinishida kiriting!\nBoshqa turdagi ma'lumotlar qabul qilinmaydi.",
            "uzk": "Миқдорни фақат рақам кўринишида киритинг!\nБошқа турдаги маълумотлар қабул қилинмайди.",
            "rus": "Количество укажите только цифрами!\nДругие данные не принимаются.",
        }.get(lang),
        reply_markup=types.ReplyKeyboardRemove(),
    )
