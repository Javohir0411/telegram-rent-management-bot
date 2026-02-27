from aiogram import Router, F, types

from database.session import get_user_language
from states import AddProductState

router = Router(name=__name__)

@router.message(AddProductState.are_there_size, F.text.casefold() == "yes")
async def handle_is_there_size_ok(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    await state.update_data(are_there_size=True)
    data = state.get_data("inserted_product_name")
    await message.answer(
        text={
            "uzl": f"{data} uchun hajmni tanlang",
            "uzl": f"{data} uchun hajmni tanlang",
            "uzl": f"{data} uchun hajmni tanlang",
        }
    )