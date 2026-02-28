from keyboards.common_keyboards import build_yes_or_no_kb
from database.session import get_user_language
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram import Router, types
from states import RentStatus
import logging

router = Router(name=__name__)


@router.message(StateFilter(RentStatus.quantity))
async def handle_product_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    logging.info(f"DATA-DAGI MA'LUMOTLAR: {data}")

    product_quantity = (message.text or "").strip()
    lang = await get_user_language(message)

    if lang == "uzl":
        invalid_message = "Iltimos, faqat raqam kiriting!"
        valid_message = "Yana biror mahsulot tanlaysizmi?"
        too_much_tpl = "❌ Xatolik: qoldiqdan ko‘proq kiritdingiz.\nQoldiq: {remaining}"
    elif lang == "uzk":
        invalid_message = "Илтимос, фақат рақам киритинг!"
        valid_message = "Яна бирор маҳсулот танлайсизми?"
        too_much_tpl = "❌ Хато: қолдиқдан кўпроқ киритдингиз.\nҚолдиқ: {remaining}"
    else:  # rus
        invalid_message = "Пожалуйста, введите только число!"
        valid_message = "Вы хотели бы выбрать другой товар?"
        too_much_tpl = "❌ Ошибка: вы ввели больше, чем остаток.\nОстаток: {remaining}"

    if not product_quantity.isdigit():
        await message.answer(text=invalid_message, reply_markup=types.ReplyKeyboardRemove())
        return

    qty = int(product_quantity)

    # QOLDIQ TEKSHIRUV (state'dan keladi)
    remaining = data.get("selected_remaining")  # sizda logda bor edi: 300
    logging.info(f"SELECTED_REMAINING: {remaining}, USER_QTY: {qty}")

    if remaining is not None and qty > int(remaining):
        await message.answer(
            text=too_much_tpl.format(remaining=remaining),
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    # Endi rent_info ga yozamiz
    rent_info = data.get("rent_info", [])
    if rent_info:
        rent_info[-1]["quantity"] = qty
        await state.update_data(rent_info=rent_info)

    logging.info(f"RENT_INFO-DAGI MA'LUMOTLAR: {rent_info}")

    await message.answer(
        text=valid_message,
        reply_markup=build_yes_or_no_kb()
    )
    await state.set_state(RentStatus.additional_choice)
