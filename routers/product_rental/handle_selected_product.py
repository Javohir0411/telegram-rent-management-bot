import logging

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import select

from bot_strings.enum_str import PRODUCT_TYPE_LABEL
from bot_strings.rent_command_strings import RentStrings
from database.products.available_product import get_available_products
from database.session import async_session_maker, get_user_language
from db.models import User
from keyboards.common_keyboards import build_select_keyboard, build_lesa_keyboard, build_taxta_keyboard, \
    build_metal_keyboard
# from keyboards.select_product_keyboard import build_products_reply_keyboard
from states import RentStatus
from utils.enums import ProductTypeEnum, ProductSizeEnum
from utils.get_user_from_db import get_user_by_telegram_or_phone

router = Router(name=__name__)


@router.message(RentStatus.product_choice)
async def handle_selected_product(message: types.Message, state: FSMContext):
    selected_product = message.text
    lang = await get_user_language(message)
    available_types = set()

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        current_user = result.scalar_one_or_none()
        await state.update_data(user_id=current_user.id)

        available_products = await get_available_products(session)
        for product, remaining_quantity in available_products:
            available_types.add(product.product_type.name)

    if selected_product not in [PRODUCT_TYPE_LABEL[lang][product_type] for product_type in ProductTypeEnum]:
        kb = [PRODUCT_TYPE_LABEL[lang][t] for t in available_types]
        logging.info(f"KB: {kb}")
        await message.answer(
            text="Илтимос, фақат қуйидаги тугмалардан танланг.",
            reply_markup=build_select_keyboard(kb),

        )
        return

    data = await state.get_data()
    rent_info = data.get("rent_info", [])
    logging.info(f"SELECTED PRODUCT: {selected_product}")
    label_to_enum = {
        label: enum_member
        for enum_member, label in PRODUCT_TYPE_LABEL[lang].items()
    }
    product_type_enum = label_to_enum[selected_product]  # ProductTypeEnum.taxta_opalubka
    rent_info.append({
        "product_type": product_type_enum.name,  # yoki .value
    })
    await state.update_data(rent_info=rent_info)

    quantity_string = RentStrings.INSERT_QUANTITY_PRODUCT[lang]
    logging.info(f"QUANTITY STRING: {quantity_string}")

    # if selected_product == ProductTypeEnum.lesa.value:
    #     await state.set_state(RentStatus.lesa_size_choice)
    #     if lang == "uzl":
    #         size = "Iltimos, lesa uchun o'lcham kiriting:"
    #     elif lang == "uzk":
    #         size = "Илтимос, леса учун ўлчам киритинг:"
    #     elif lang == "rus":
    #         size = "Пожалуйста, укажите размер лесы:"
    #
    #     await message.answer(
    #         text=size,
    #         reply_markup=build_lesa_keyboard(lang)
    #     )

    if selected_product in [PRODUCT_TYPE_LABEL[lang][product_type.taxta_opalubka.value] for product_type in
                            ProductTypeEnum]:
        logging.info(f"SELECTED Pro PRODUCT: {selected_product}")
        logging.info(f"PRODUCT TYPE LABEL [LANG]: {PRODUCT_TYPE_LABEL[lang]}")
        await state.set_state(RentStatus.taxta_size_choice)
        if lang == "uzl":
            size = "Iltimos, taxta opalubka uchun o'lcham kiriting:"
        elif lang == "uzk":
            size = "Илтимос, тахта опалубка учун ўлчам киритинг:"
        elif lang == "rus":
            size = "Пожалуйста, укажите размер дощатая опалубка:"

        await state.set_state(RentStatus.taxta_size_choice)
        await message.answer(
            text=size,
            reply_markup=build_taxta_keyboard(lang)
        )

    elif selected_product in [PRODUCT_TYPE_LABEL[lang][product_type.metal_opalubka.value] for product_type in
                              ProductTypeEnum]:

        if lang == "uzl":
            size = "Iltimos, metal opalubka uchun o'lcham kiriting:"
        elif lang == "uzk":
            size = "Илтимос, метал опалубка учун ўлчам киритинг:"
        elif lang == "rus":
            size = "Пожалуйста, укажите размер металлическая опалубка:"

        await state.set_state(RentStatus.metal_size_choice)
        await message.answer(
            text=size,
            reply_markup=build_metal_keyboard(lang)
        )



    else:
        # Monolit yoki Taxta → miqdor kiritish
        await state.set_state(RentStatus.quantity)
        await message.answer(
            text=quantity_string,
            reply_markup=ReplyKeyboardRemove()
        )

# Lesa-ni hozircha faqat bitta hajmi mavjud ekan, yangilari qo'shilganida o'lcham ham kiritiladi
