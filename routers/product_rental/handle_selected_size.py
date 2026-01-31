import logging
from aiogram.filters import StateFilter

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot_strings.enum_str import SIZE_LABEL
from bot_strings.rent_command_strings import RentStrings
from database.session import async_session_maker, get_user_language
from keyboards.common_keyboards import build_select_keyboard, build_lesa_keyboard, build_taxta_keyboard, \
    build_metal_keyboard, TAXTA_SIZES, LESA_SIZES, METAL_SIZES
from states import RentStatus
from utils.enums import ProductSizeEnum
from utils.get_user_from_db import get_user_by_telegram_or_phone

router = Router(name=__name__)


# @router.message(StateFilter(RentStatus.lesa_size_choice))
# @router.message(StateFilter(RentStatus.taxta_size_choice))
# @router.message(StateFilter(RentStatus.metal_size_choice))
# async def handle_selected_size(message: types.Message, state: FSMContext):
#     selected_size = message.text
#     lang = await get_user_language(message)
#     text_size = RentStrings.INSERT_INVALID_SIZE[lang]
#     text_quantity = RentStrings.INSERT_QUANTITY_PRODUCT[lang]
#
#     current_state = await state.get_state()
#
#     text_to_enum = {SIZE_LABEL[lang][e]: e.value for e in ProductSizeEnum}
#
#     if selected_size in text_to_enum:
#         enum_value = text_to_enum[selected_size]
#
#         data = await state.get_data()
#         rent_info = data.get("rent_info", [])
#
#         if rent_info:
#             # Oxirgi mahsulotga size qo'shamiz
#             rent_info[-1]["product_size"] = enum_value
#             await state.update_data(rent_info=rent_info)
#
#         await state.set_state(RentStatus.quantity)
#         await message.answer(text=text_quantity, reply_markup=ReplyKeyboardRemove())
#     else:
#         if current_state == RentStatus.lesa_size_choice.state:
#             await message.answer(text=text_size, reply_markup=build_lesa_keyboard(lang))
#         elif current_state == RentStatus.taxta_size_choice.state:
#             await message.answer(text=text_size, reply_markup=build_taxta_keyboard(lang))
#         elif current_state == RentStatus.metal_size_choice.state:
#             await message.answer(text=text_size, reply_markup=build_metal_keyboard(lang))

@router.message(StateFilter(RentStatus.lesa_size_choice))
@router.message(StateFilter(RentStatus.taxta_size_choice))
@router.message(StateFilter(RentStatus.metal_size_choice))
async def handle_selected_size(message: types.Message, state: FSMContext):
    selected_size = (message.text or "").strip()
    lang = await get_user_language(message)

    text_size = RentStrings.INSERT_INVALID_SIZE[lang]
    text_quantity = RentStrings.INSERT_QUANTITY_PRODUCT[lang]

    current_state = await state.get_state()

    if current_state == RentStatus.lesa_size_choice.state:
        allowed_sizes = LESA_SIZES
        kb = build_lesa_keyboard(lang)
    elif current_state == RentStatus.taxta_size_choice.state:
        allowed_sizes = TAXTA_SIZES
        kb = build_taxta_keyboard(lang)
    elif current_state == RentStatus.metal_size_choice.state:
        allowed_sizes = METAL_SIZES
        kb = build_metal_keyboard(lang)
    else:
        allowed_sizes = ()
        kb = ReplyKeyboardRemove()

    text_to_enum = {SIZE_LABEL[lang][e]: e.value for e in allowed_sizes}

    if selected_size in text_to_enum:
        enum_value = text_to_enum[selected_size]

        data = await state.get_data()
        rent_info = data.get("rent_info", [])
        if rent_info:
            rent_info[-1]["product_size"] = enum_value
            await state.update_data(rent_info=rent_info)

        await state.set_state(RentStatus.quantity)
        await message.answer(text=text_quantity, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(text=text_size, reply_markup=kb)
